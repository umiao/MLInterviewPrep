#!/usr/bin/env pwsh
<#
.SYNOPSIS
    PowerShell autonomous task runner. Mirror of scripts/autonomous_run.sh
    with Windows-native process handling and without the SIGPIPE death
    mode that kills the bash version when launched from inside Claude Code's
    background subprocess capture (see comments below).

.DESCRIPTION
    Runs claude -p sessions in a loop. Each session starts with a fresh
    context, picks ONE highest-priority unblocked task from TASKS.md / tasks.db,
    completes it, commits, and exits. The orchestrator starts the next session
    with fresh context until MAX_SESSIONS is reached OR all_done flag is set
    in .claude/session_state.json.

    Every line of output goes to BOTH the console AND logs/autonomous.log,
    so progress is preserved even if the console is detached.

.PARAMETER MaxSessions
    Maximum number of sequential sessions to run. Default: 5.

.EXAMPLE
    .\scripts\autonomous_run.ps1 8
    Run up to 8 sessions.

.EXAMPLE
    pwsh -File scripts/autonomous_run.ps1 6
    Same, invoked explicitly (works from cmd.exe or bash).

.NOTES
    Why PowerShell instead of bash for this script path:

    The bash version (scripts/autonomous_run.sh) has an emergent failure mode
    when launched via Claude Code's run_in_background subprocess capture: after
    the first inner "claude -p" session returns, the orchestrator's next
    "echo '[orchestrator] Session ended. Continuing...'" statement hits a
    SIGPIPE because the captured stdout fd has been closed by the harness,
    and "set -e" terminates the parent bash. The symptom is "commits land
    but the orchestrator dies after 1 task". Confirmed forensically on
    2026-04-11: the bash orchestrator stopped writing to its output buffer
    4 seconds after launch (during "Session 1/N" echo), while the inner
    claude -p session kept working for 15 more minutes and successfully
    committed T-P1-359 at 17:28:44 -- then the parent bash died silently
    on its first echo after the subprocess returned.

    PowerShell does not have this issue when launched from a user terminal,
    because PowerShell does not couple Write-Host to a specific OS stdio
    fd in the same way bash echo does, and Start-Process with -Wait does
    not forward SIGPIPE-style failures to the parent.
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [int]$MaxSessions = 5
)

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# Navigate to repo root (script is at scripts/autonomous_run.ps1)
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$LockFile    = Join-Path $RepoRoot '.claude\autonomous.lock'
$LogDir      = Join-Path $RepoRoot 'logs'
$LogFile     = Join-Path $LogDir 'autonomous.log'
$StateFile   = Join-Path $RepoRoot '.claude\session_state.json'

# Ensure log dir exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message)
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    Write-Host $line
    Add-Content -LiteralPath $LogFile -Value $line -Encoding utf8
}

# ---------------------------------------------------------------------------
# Concurrent-run protection (PID lockfile)
# ---------------------------------------------------------------------------

if (Test-Path $LockFile) {
    $existingPid = Get-Content $LockFile -ErrorAction SilentlyContinue
    if ($existingPid -and (Get-Process -Id $existingPid -ErrorAction SilentlyContinue)) {
        Write-Log "[orchestrator] Another instance is running (PID $existingPid). Exiting."
        exit 1
    }
    Write-Log "[orchestrator] Found stale lockfile (PID $existingPid no longer alive) -- removing"
    Remove-Item $LockFile -Force
}

$PID | Out-File -LiteralPath $LockFile -Encoding ascii -NoNewline

# Cleanup on any exit path (Ctrl+C, error, normal completion)
$cleanup = {
    if (Test-Path $LockFile) {
        Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
    }
    Write-Log "[orchestrator] Lockfile released"
}
# PowerShell doesn't have a clean "trap EXIT" equivalent, so we wrap the
# main body in try/finally.

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

$sessionCount = 0
$consecutiveFailures = 0
$MaxConsecutiveFailures = 2

Write-Log "[orchestrator] Starting autonomous run (max $MaxSessions sessions)"
Write-Log "[orchestrator] Repo: $RepoRoot"
Write-Log "[orchestrator] Log:  $LogFile"
Write-Log "[orchestrator] Progress: check git log, PROGRESS.md, TASKS.md"
Write-Log "[orchestrator] Press Ctrl+C to stop. Work is saved after each task."
Write-Log ""

try {
    while ($sessionCount -lt $MaxSessions) {
        $sessionCount++
        Write-Log "--- Session $sessionCount/$MaxSessions ---"

        # Capture commit SHA before session for progress detection
        $startSha = (git rev-parse HEAD 2>$null).Trim()
        if (-not $startSha) {
            Write-Log "[orchestrator] git rev-parse failed -- is this a git repo? Exiting."
            exit 1
        }

        # Build claude -p prompt
        $prompt = @"
Autonomous mode. Read TASKS.md, pick ONE highest-priority unblocked task, and complete it. After completing the task: 1) run tests, 2) update PROGRESS.md and TASKS.md, 3) git commit with message format '[T-XX-N] description', 4) update .claude/session_state.json, then stop. If no unblocked tasks remain, set all_done=true in session_state.json and stop.
"@

        # Invoke claude -p. Use & operator (native command invocation).
        # Exit code is captured via $LASTEXITCODE.
        #
        # --allowedTools matches the bash version.
        # --max-turns bounds each session to prevent runaway execution.
        & claude -p $prompt `
            --allowedTools "Read,Write,Edit,Bash,Glob,Grep,Task" `
            --max-turns 200
        $sessionExitCode = $LASTEXITCODE

        if ($sessionExitCode -eq 0) {
            $consecutiveFailures = 0

            # Check if all tasks done via the state file
            $allDone = $false
            if (Test-Path $StateFile) {
                try {
                    $state = Get-Content $StateFile -Raw -Encoding utf8 | ConvertFrom-Json
                    if ($state.PSObject.Properties.Name -contains 'all_done') {
                        $allDone = [bool]$state.all_done
                    }
                } catch {
                    Write-Log "[orchestrator] Could not parse session_state.json (continuing): $_"
                }
            }

            if ($allDone) {
                Write-Log "[orchestrator] all_done=true in session_state.json -- all tasks complete!"
                break
            }
            Write-Log "[orchestrator] Session $sessionCount ended (exit 0). Continuing to next session..."
        }
        else {
            # Session failed. Stash any in-progress changes so the next
            # session starts clean.
            Write-Log "[orchestrator] Session $sessionCount failed (exit $sessionExitCode)"
            git stash push -m "auto-stash: failed session $sessionCount" 2>&1 | ForEach-Object { Write-Log "  git: $_" }

            # Distinguish context exhaustion (some commits happened) from real
            # failure (no commits). If the session made ANY commits, the work
            # is progressing, not failing.
            $currentSha = (git rev-parse HEAD 2>$null).Trim()
            if ($currentSha -ne $startSha) {
                Write-Log "[orchestrator] Session made progress (new commits: $startSha -> $currentSha). Not counting as failure."
                $consecutiveFailures = 0
            }
            else {
                $consecutiveFailures++
                Write-Log "[orchestrator] Consecutive failures: $consecutiveFailures/$MaxConsecutiveFailures"
                if ($consecutiveFailures -ge $MaxConsecutiveFailures) {
                    Write-Log "[orchestrator] Too many consecutive failures. Stopping."
                    break
                }
            }
        }

        Write-Log ""
    }

    Write-Log ""
    Write-Log "[orchestrator] Finished after $sessionCount session(s)"
    Write-Log "[orchestrator] Review:  git log --oneline -20"
    Write-Log "[orchestrator] Status:  Get-Content TASKS.md"
    Write-Log "[orchestrator] Log:     Get-Content logs\autonomous.log"
}
finally {
    & $cleanup
}
