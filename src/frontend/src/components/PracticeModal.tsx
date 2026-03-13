import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiRequestError } from "../utils/api";
import type { AttemptCreate, AttemptResult, Problem } from "../types/problem";

const RESULTS: { value: AttemptResult; label: string }[] = [
  { value: "solved", label: "Solved" },
  { value: "hint", label: "Needed Hint" },
  { value: "failed", label: "Failed" },
  { value: "timeout", label: "Timeout" },
];

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

interface Props {
  problem: Problem;
  onClose: () => void;
  onSubmitted: () => void;
}

export default function PracticeModal({ problem, onClose, onSubmitted }: Props) {
  // Timer state
  const [elapsed, setElapsed] = useState(0);
  const [running, setRunning] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Form state
  const [result, setResult] = useState<AttemptResult>("solved");
  const [approachNotes, setApproachNotes] = useState("");
  const [complexityTime, setComplexityTime] = useState("");
  const [complexitySpace, setComplexitySpace] = useState("");
  const [comfort, setComfort] = useState(3);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Timer logic
  const startTimer = useCallback(() => {
    if (running) return;
    setRunning(true);
  }, [running]);

  const pauseTimer = useCallback(() => {
    setRunning(false);
  }, []);

  const resetTimer = useCallback(() => {
    setRunning(false);
    setElapsed(0);
  }, []);

  useEffect(() => {
    if (running) {
      intervalRef.current = setInterval(() => {
        setElapsed((prev) => prev + 1);
      }, 1000);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [running]);

  // Close on Escape
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [onClose]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    pauseTimer();

    const payload: AttemptCreate = {
      duration_seconds: elapsed > 0 ? elapsed : null,
      result,
      approach_notes: approachNotes.trim() || null,
      complexity_time: complexityTime.trim() || null,
      complexity_space: complexitySpace.trim() || null,
      comfort_after: comfort,
    };

    try {
      await api.post(`/problems/${problem.id}/attempts`, payload);
      onSubmitted();
    } catch (err) {
      const msg =
        err instanceof ApiRequestError ? err.message : String(err);
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div className="min-w-0">
            <h2 className="text-lg font-semibold truncate">{problem.title}</h2>
            <div className="flex items-center gap-2 text-sm text-gray-500 mt-0.5">
              {problem.leetcode_id && <span>#{problem.leetcode_id}</span>}
              {problem.difficulty && (
                <span className="capitalize">{problem.difficulty}</span>
              )}
              {problem.pattern && <span>| {problem.pattern}</span>}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none px-2"
            title="Close"
          >
            x
          </button>
        </div>

        {/* Timer */}
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center gap-4">
            <span className="text-3xl font-mono font-bold tabular-nums">
              {formatTime(elapsed)}
            </span>
            <div className="flex gap-2">
              {!running ? (
                <button
                  type="button"
                  onClick={startTimer}
                  className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                >
                  {elapsed > 0 ? "Resume" : "Start"}
                </button>
              ) : (
                <button
                  type="button"
                  onClick={pauseTimer}
                  className="px-3 py-1 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600"
                >
                  Pause
                </button>
              )}
              <button
                type="button"
                onClick={resetTimer}
                className="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
              >
                Reset
              </button>
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-4">
          {/* Approach notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Approach Notes
            </label>
            <textarea
              value={approachNotes}
              onChange={(e) => setApproachNotes(e.target.value)}
              rows={5}
              placeholder="Describe your approach, key insights, mistakes..."
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm resize-y focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Result + Complexity row */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Result
              </label>
              <select
                value={result}
                onChange={(e) => setResult(e.target.value as AttemptResult)}
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
              >
                {RESULTS.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Time Complexity
              </label>
              <input
                type="text"
                value={complexityTime}
                onChange={(e) => setComplexityTime(e.target.value)}
                placeholder="e.g. O(n log n)"
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Space Complexity
              </label>
              <input
                type="text"
                value={complexitySpace}
                onChange={(e) => setComplexitySpace(e.target.value)}
                placeholder="e.g. O(n)"
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
              />
            </div>
          </div>

          {/* Comfort slider */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Comfort Level: {comfort}/5
            </label>
            <input
              type="range"
              min={1}
              max={5}
              step={1}
              value={comfort}
              onChange={(e) => setComfort(Number(e.target.value))}
              className="w-full accent-blue-600"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-0.5">
              <span>1 - Lost</span>
              <span>2 - Struggled</span>
              <span>3 - OK</span>
              <span>4 - Good</span>
              <span>5 - Easy</span>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-50 text-red-700 px-3 py-2 rounded text-sm">
              {error}
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm border border-gray-300 rounded hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {submitting ? "Submitting..." : "Submit Attempt"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
