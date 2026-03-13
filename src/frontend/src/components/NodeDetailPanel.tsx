import { useCallback, useEffect, useState } from "react";
import { api } from "../utils/api";
import { useApi, useMutation } from "../hooks/useApi";
import type { FrameworkNode, NodeStatus, StudyLog } from "../types/framework";

const STATUS_OPTIONS: { value: NodeStatus; label: string; color: string }[] = [
  { value: "not_started", label: "Not Started", color: "bg-red-100 text-red-700" },
  { value: "in_progress", label: "In Progress", color: "bg-yellow-100 text-yellow-700" },
  { value: "review", label: "Review", color: "bg-blue-100 text-blue-700" },
  { value: "mastered", label: "Mastered", color: "bg-green-100 text-green-700" },
];

const ACTIVITY_TYPES = [
  "Reading",
  "Practice",
  "Video/Lecture",
  "Flashcards",
  "Mock Interview",
  "Project",
  "Other",
];

interface Props {
  node: FrameworkNode;
  onNodeUpdated: () => void;
}

/** Full node detail panel with editable status/confidence, study log form, and history. */
export default function NodeDetailPanel({ node, onNodeUpdated }: Props) {
  // -- Editable fields --
  const [editStatus, setEditStatus] = useState<NodeStatus>(node.status);
  const [editConfidence, setEditConfidence] = useState(node.confidence_level);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState("");

  // Sync local state when node changes
  useEffect(() => {
    setEditStatus(node.status);
    setEditConfidence(node.confidence_level);
    setSaveMsg("");
  }, [node.id, node.status, node.confidence_level]);

  const handleSaveNode = useCallback(async () => {
    if (editStatus === node.status && editConfidence === node.confidence_level) return;
    setSaving(true);
    setSaveMsg("");
    try {
      await api.put(`/framework/nodes/${node.id}`, {
        status: editStatus,
        confidence_level: editConfidence,
      });
      setSaveMsg("Saved");
      onNodeUpdated();
    } catch {
      setSaveMsg("Error saving");
    } finally {
      setSaving(false);
    }
  }, [node.id, node.status, node.confidence_level, editStatus, editConfidence, onNodeUpdated]);

  // -- Study log form --
  const [logDate, setLogDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [logDuration, setLogDuration] = useState(30);
  const [logActivity, setLogActivity] = useState("");
  const [logNotes, setLogNotes] = useState("");
  const { execute: submitLog, loading: logSubmitting } = useMutation<StudyLog>(
    "POST",
    `/framework/nodes/${node.id}/log`,
  );
  const [logMsg, setLogMsg] = useState("");

  // Reset log form when node changes
  useEffect(() => {
    setLogMsg("");
  }, [node.id]);

  const handleSubmitLog = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setLogMsg("");
    try {
      await submitLog({
        date: logDate,
        duration_minutes: logDuration,
        activity_type: logActivity || null,
        notes: logNotes || null,
      });
      setLogMsg("Logged");
      setLogDuration(30);
      setLogNotes("");
      onNodeUpdated();
      // Refetch logs
      setLogsKey((k) => k + 1);
    } catch {
      setLogMsg("Error logging");
    }
  }, [logDate, logDuration, logActivity, logNotes, submitLog, onNodeUpdated]);

  // -- Study history --
  const [logsKey, setLogsKey] = useState(0);
  const { data: logs, loading: logsLoading } = useApi<StudyLog[]>(
    `/framework/nodes/${node.id}/logs`,
    { params: { limit: 10, _r: logsKey } },
  );

  const hasChanges = editStatus !== node.status || editConfidence !== node.confidence_level;

  return (
    <div className="space-y-4">
      {/* Node info */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-1">
          Selected Node
        </h3>
        <p className="text-lg font-semibold text-gray-800">{node.title}</p>
        <p className="text-xs text-gray-400 font-mono mt-0.5 truncate" title={node.path}>
          {node.path}
        </p>

        <div className="mt-3 space-y-2 text-sm">
          {/* Status selector */}
          <div>
            <label className="block text-gray-500 text-xs mb-1">Status</label>
            <select
              value={editStatus}
              onChange={(e) => setEditStatus(e.target.value as NodeStatus)}
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              {STATUS_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Confidence slider */}
          <div>
            <label className="block text-gray-500 text-xs mb-1">
              Confidence: {editConfidence}/5
            </label>
            <input
              type="range"
              min={0}
              max={5}
              value={editConfidence}
              onChange={(e) => setEditConfidence(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-0.5">
              <span>0</span><span>5</span>
            </div>
          </div>

          {/* Save button */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleSaveNode}
              disabled={!hasChanges || saving}
              className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-40 transition-colors"
            >
              {saving ? "Saving..." : "Save"}
            </button>
            {saveMsg && (
              <span className={`text-xs ${saveMsg === "Saved" ? "text-green-600" : "text-red-600"}`}>
                {saveMsg}
              </span>
            )}
          </div>

          <hr className="border-gray-100" />

          {/* Read-only fields */}
          <div className="flex justify-between">
            <span className="text-gray-500">Progress</span>
            <span className="font-medium">{Math.round(node.progress_pct)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Importance</span>
            <span className="font-medium">{node.importance}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Priority</span>
            <span className="font-medium">{node.priority}</span>
          </div>
          {node.estimated_hours != null && (
            <div className="flex justify-between">
              <span className="text-gray-500">Est. Hours</span>
              <span className="font-medium">{node.estimated_hours}h</span>
            </div>
          )}
        </div>
      </div>

      {/* Study log form */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
          Log Study Session
        </h3>
        <form onSubmit={handleSubmitLog} className="space-y-2">
          <div>
            <label className="block text-gray-500 text-xs mb-0.5">Date</label>
            <input
              type="date"
              value={logDate}
              onChange={(e) => setLogDate(e.target.value)}
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
              required
            />
          </div>
          <div>
            <label className="block text-gray-500 text-xs mb-0.5">Duration (min)</label>
            <input
              type="number"
              min={1}
              value={logDuration}
              onChange={(e) => setLogDuration(Number(e.target.value))}
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
              required
            />
          </div>
          <div>
            <label className="block text-gray-500 text-xs mb-0.5">Activity Type</label>
            <select
              value={logActivity}
              onChange={(e) => setLogActivity(e.target.value)}
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option value="">-- Optional --</option>
              {ACTIVITY_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-gray-500 text-xs mb-0.5">Notes</label>
            <textarea
              value={logNotes}
              onChange={(e) => setLogNotes(e.target.value)}
              rows={2}
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none"
              placeholder="Optional notes..."
            />
          </div>
          <div className="flex items-center gap-2">
            <button
              type="submit"
              disabled={logSubmitting}
              className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-40 transition-colors"
            >
              {logSubmitting ? "Logging..." : "Log Session"}
            </button>
            {logMsg && (
              <span className={`text-xs ${logMsg === "Logged" ? "text-green-600" : "text-red-600"}`}>
                {logMsg}
              </span>
            )}
          </div>
        </form>
      </div>

      {/* Study history */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
          Study History
        </h3>
        {logsLoading ? (
          <p className="text-xs text-gray-400">Loading...</p>
        ) : !logs || logs.length === 0 ? (
          <p className="text-xs text-gray-400">No study sessions yet.</p>
        ) : (
          <div className="space-y-2">
            {logs.map((log) => (
              <div key={log.id} className="border-l-2 border-blue-300 pl-2 py-0.5">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600 font-medium">{log.date}</span>
                  <span className="text-gray-500">{log.duration_minutes}m</span>
                </div>
                {log.activity_type && (
                  <span className="text-xs text-blue-600">{log.activity_type}</span>
                )}
                {log.notes && (
                  <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{log.notes}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
