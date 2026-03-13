import { useCallback, useEffect, useRef, useState } from "react";

interface UseTimerResult {
  /** Elapsed time in seconds. */
  elapsed: number;
  /** Whether the timer is currently running. */
  running: boolean;
  /** Start or resume the timer. */
  start: () => void;
  /** Pause the timer (preserves elapsed time). */
  pause: () => void;
  /** Reset elapsed time to 0 and stop the timer. */
  reset: () => void;
}

/**
 * Simple stopwatch hook for problem practice sessions.
 *
 * Usage:
 *   const { elapsed, running, start, pause, reset } = useTimer();
 */
export function useTimer(): UseTimerResult {
  const [elapsed, setElapsed] = useState(0);
  const [running, setRunning] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearTimer = useCallback(() => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const start = useCallback(() => {
    setRunning(true);
  }, []);

  const pause = useCallback(() => {
    setRunning(false);
    clearTimer();
  }, [clearTimer]);

  const reset = useCallback(() => {
    setRunning(false);
    clearTimer();
    setElapsed(0);
  }, [clearTimer]);

  useEffect(() => {
    if (running) {
      intervalRef.current = setInterval(() => {
        setElapsed((prev) => prev + 1);
      }, 1000);
    } else {
      clearTimer();
    }
    return clearTimer;
  }, [running, clearTimer]);

  return { elapsed, running, start, pause, reset };
}
