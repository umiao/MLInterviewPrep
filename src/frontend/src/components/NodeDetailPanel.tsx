import { useCallback, useEffect, useRef, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import { api } from "../utils/api";
import { useToast } from "../contexts/ToastContext";
import { useDebounce } from "../hooks/useDebounce";
import Tabs from "./ui/Tabs";
import ListenButton from "./ui/ListenButton";
import type { FrameworkNode, NodeStatus, StudyLog } from "../types/framework";
import type { Problem } from "../types/problem";
import type { InterviewQuestion } from "../types/question";

const STATUS_OPTIONS: { value: NodeStatus; label: string }[] = [
  { value: "not_started", label: "Not Started" },
  { value: "in_progress", label: "In Progress" },
  { value: "review", label: "Review" },
  { value: "mastered", label: "Mastered" },
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

const TABS = [
  { key: "details", label: "Details" },
  { key: "notes", label: "Notes" },
  { key: "problems", label: "Problems" },
  { key: "questions", label: "Questions" },
  { key: "log", label: "Study Log" },
];

interface Props {
  node: FrameworkNode;
  onNodeUpdated: () => void;
}

/** Full node detail panel with tabs: Details, Notes (markdown), Study Log. */
export default function NodeDetailPanel({ node, onNodeUpdated }: Props) {
  const queryClient = useQueryClient();
  const toast = useToast();

  // -- Inline title edit --
  const [editingTitle, setEditingTitle] = useState(false);
  const [titleDraft, setTitleDraft] = useState(node.title);
  const titleInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setEditingTitle(false);
    setTitleDraft(node.title);
  }, [node.id, node.title]);

  useEffect(() => {
    if (editingTitle) titleInputRef.current?.focus();
  }, [editingTitle]);

  const saveTitleMutation = useMutation({
    mutationFn: (newTitle: string) =>
      api.put(`/framework/nodes/${node.id}`, { title: newTitle }),
    onSuccess: () => {
      onNodeUpdated();
      toast.success("Title updated");
    },
    onError: () => toast.error("Failed to update title"),
  });

  const handleTitleSubmit = useCallback(() => {
    const trimmed = titleDraft.trim();
    if (!trimmed || trimmed === node.title) {
      setTitleDraft(node.title);
      setEditingTitle(false);
      return;
    }
    saveTitleMutation.mutate(trimmed);
    setEditingTitle(false);
  }, [titleDraft, node.title, saveTitleMutation]);

  const handleTitleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        e.preventDefault();
        handleTitleSubmit();
      } else if (e.key === "Escape") {
        setTitleDraft(node.title);
        setEditingTitle(false);
      }
    },
    [handleTitleSubmit, node.title],
  );

  // -- Editable fields (Details tab) --
  const [editStatus, setEditStatus] = useState<NodeStatus>(node.status);
  const [editConfidence, setEditConfidence] = useState(node.confidence_level);
  const [saveMsg, setSaveMsg] = useState("");

  useEffect(() => {
    setEditStatus(node.status);
    setEditConfidence(node.confidence_level);
    setSaveMsg("");
  }, [node.id, node.status, node.confidence_level]);

  const saveNodeMutation = useMutation({
    mutationFn: () =>
      api.put(`/framework/nodes/${node.id}`, {
        status: editStatus,
        confidence_level: editConfidence,
      }),
    onSuccess: () => {
      setSaveMsg("Saved");
      onNodeUpdated();
      toast.success("Node updated");
    },
    onError: () => {
      setSaveMsg("Error saving");
      toast.error("Failed to save node");
    },
  });

  const handleSaveNode = useCallback(() => {
    if (editStatus === node.status && editConfidence === node.confidence_level) return;
    setSaveMsg("");
    saveNodeMutation.mutate();
  }, [node.status, node.confidence_level, editStatus, editConfidence, saveNodeMutation]);

  const saving = saveNodeMutation.isPending;
  const hasChanges = editStatus !== node.status || editConfidence !== node.confidence_level;

  // -- Notes tab (markdown edit/preview + autosave) --
  const [notesDraft, setNotesDraft] = useState(node.description ?? "");
  const [notesPreview, setNotesPreview] = useState(false);
  const [notesSaveStatus, setNotesSaveStatus] = useState<"" | "saving" | "saved" | "error">("");

  // Track the node id we initialized notes for to avoid stale resets
  const notesNodeIdRef = useRef(node.id);

  useEffect(() => {
    if (node.id !== notesNodeIdRef.current) {
      notesNodeIdRef.current = node.id;
      setNotesDraft(node.description ?? "");
      setNotesPreview(false);
      setNotesSaveStatus("");
    }
  }, [node.id, node.description]);

  const debouncedNotes = useDebounce(notesDraft, 500);

  const saveNotesMutation = useMutation({
    mutationFn: (description: string) =>
      api.put(`/framework/nodes/${node.id}`, { description }),
    onSuccess: () => {
      setNotesSaveStatus("saved");
      onNodeUpdated();
    },
    onError: () => {
      setNotesSaveStatus("error");
      toast.error("Failed to save notes");
    },
  });

  // Track the last saved notes to avoid redundant saves
  const lastSavedNotesRef = useRef(node.description ?? "");

  useEffect(() => {
    if (node.id !== notesNodeIdRef.current) return;
    if (debouncedNotes === lastSavedNotesRef.current) return;
    lastSavedNotesRef.current = debouncedNotes;
    setNotesSaveStatus("saving");
    saveNotesMutation.mutate(debouncedNotes);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedNotes, node.id]);

  // -- Study log form (Study Log tab) --
  const [logDate, setLogDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [logDuration, setLogDuration] = useState(30);
  const [logActivity, setLogActivity] = useState("");
  const [logNotes, setLogNotes] = useState("");
  const [logMsg, setLogMsg] = useState("");

  const submitLogMutation = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      api.post<StudyLog>(`/framework/nodes/${node.id}/log`, body),
    onSuccess: () => {
      setLogMsg("Logged");
      setLogDuration(30);
      setLogNotes("");
      onNodeUpdated();
      queryClient.invalidateQueries({ queryKey: ["framework", "nodes", node.id, "logs"] });
      toast.success("Study session logged");
    },
    onError: () => {
      setLogMsg("Error logging");
      toast.error("Failed to log study session");
    },
  });

  const logSubmitting = submitLogMutation.isPending;

  useEffect(() => {
    setLogMsg("");
  }, [node.id]);

  const handleSubmitLog = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      setLogMsg("");
      submitLogMutation.mutate({
        date: logDate,
        duration_minutes: logDuration,
        activity_type: logActivity || null,
        notes: logNotes || null,
      });
    },
    [logDate, logDuration, logActivity, logNotes, submitLogMutation],
  );

  // -- Study history --
  const { data: logs, isLoading: logsLoading } = useQuery({
    queryKey: ["framework", "nodes", node.id, "logs"],
    queryFn: () =>
      api.get<StudyLog[]>(`/framework/nodes/${node.id}/logs`, { params: { limit: 10 } }),
  });

  return (
    <div className="space-y-3">
      {/* Node header with inline title edit */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        {editingTitle ? (
          <input
            ref={titleInputRef}
            value={titleDraft}
            onChange={(e) => setTitleDraft(e.target.value)}
            onBlur={handleTitleSubmit}
            onKeyDown={handleTitleKeyDown}
            className="text-lg font-semibold text-gray-800 w-full border border-blue-300 rounded px-1 py-0.5 focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        ) : (
          <h3
            className="text-lg font-semibold text-gray-800 cursor-pointer hover:text-blue-600 transition-colors"
            onClick={() => setEditingTitle(true)}
            title="Click to edit title"
          >
            {node.title}
          </h3>
        )}
        <p className="text-xs text-gray-400 font-mono mt-0.5 truncate" title={node.path}>
          {node.path}
        </p>
      </div>

      {/* Tabbed content */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <Tabs tabs={TABS} defaultTab="details">
          {(activeTab) => (
            <>
              {activeTab === "details" && (
                <DetailsTab
                  node={node}
                  editStatus={editStatus}
                  setEditStatus={setEditStatus}
                  editConfidence={editConfidence}
                  setEditConfidence={setEditConfidence}
                  hasChanges={hasChanges}
                  saving={saving}
                  saveMsg={saveMsg}
                  onSave={handleSaveNode}
                />
              )}
              {activeTab === "notes" && (
                <NotesTab
                  notesDraft={notesDraft}
                  setNotesDraft={setNotesDraft}
                  notesPreview={notesPreview}
                  setNotesPreview={setNotesPreview}
                  notesSaveStatus={notesSaveStatus}
                />
              )}
              {activeTab === "problems" && <LinkedProblemsTab nodeId={node.id} />}
              {activeTab === "questions" && <LinkedQuestionsTab nodeId={node.id} />}
              {activeTab === "log" && (
                <StudyLogTab
                  logDate={logDate}
                  setLogDate={setLogDate}
                  logDuration={logDuration}
                  setLogDuration={setLogDuration}
                  logActivity={logActivity}
                  setLogActivity={setLogActivity}
                  logNotes={logNotes}
                  setLogNotes={setLogNotes}
                  logMsg={logMsg}
                  logSubmitting={logSubmitting}
                  onSubmit={handleSubmitLog}
                  logs={logs ?? []}
                  logsLoading={logsLoading}
                />
              )}
            </>
          )}
        </Tabs>
      </div>
    </div>
  );
}

// ---- Details Tab ----

interface DetailsTabProps {
  node: FrameworkNode;
  editStatus: NodeStatus;
  setEditStatus: (s: NodeStatus) => void;
  editConfidence: number;
  setEditConfidence: (n: number) => void;
  hasChanges: boolean;
  saving: boolean;
  saveMsg: string;
  onSave: () => void;
}

function DetailsTab({
  node,
  editStatus,
  setEditStatus,
  editConfidence,
  setEditConfidence,
  hasChanges,
  saving,
  saveMsg,
  onSave,
}: DetailsTabProps) {
  return (
    <div className="space-y-2 text-sm">
      {/* Status selector */}
      <div>
        <label className="block text-gray-500 text-xs mb-1">Status</label>
        <select
          value={editStatus}
          onChange={(e) => setEditStatus(e.target.value as NodeStatus)}
          className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
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
          <span>0</span>
          <span>5</span>
        </div>
      </div>

      {/* Save button */}
      <div className="flex items-center gap-2">
        <button
          onClick={onSave}
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

      {/* Listen button */}
      {node.description && (
        <ListenButton contentType="framework_node" contentId={node.id} />
      )}

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
  );
}

// ---- Notes Tab ----

interface NotesTabProps {
  notesDraft: string;
  setNotesDraft: (s: string) => void;
  notesPreview: boolean;
  setNotesPreview: (b: boolean) => void;
  notesSaveStatus: "" | "saving" | "saved" | "error";
}

function NotesTab({
  notesDraft,
  setNotesDraft,
  notesPreview,
  setNotesPreview,
  notesSaveStatus,
}: NotesTabProps) {
  return (
    <div className="space-y-2">
      {/* Toolbar: Edit/Preview toggle + save status */}
      <div className="flex items-center justify-between">
        <div className="flex bg-gray-100 rounded p-0.5">
          <button
            onClick={() => setNotesPreview(false)}
            className={`px-2 py-0.5 text-xs font-medium rounded transition-colors ${
              !notesPreview ? "bg-white text-gray-800 shadow-sm" : "text-gray-500"
            }`}
          >
            Edit
          </button>
          <button
            onClick={() => setNotesPreview(true)}
            className={`px-2 py-0.5 text-xs font-medium rounded transition-colors ${
              notesPreview ? "bg-white text-gray-800 shadow-sm" : "text-gray-500"
            }`}
          >
            Preview
          </button>
        </div>
        <span
          className={`text-xs ${
            notesSaveStatus === "saving"
              ? "text-gray-400"
              : notesSaveStatus === "saved"
                ? "text-green-600"
                : notesSaveStatus === "error"
                  ? "text-red-600"
                  : ""
          }`}
        >
          {notesSaveStatus === "saving"
            ? "Saving..."
            : notesSaveStatus === "saved"
              ? "Saved"
              : notesSaveStatus === "error"
                ? "Save failed"
                : ""}
        </span>
      </div>

      {/* Editor or preview */}
      {notesPreview ? (
        <div className="prose prose-sm max-w-none min-h-[120px] text-sm text-gray-700 break-words">
          {notesDraft ? (
            <ReactMarkdown>{notesDraft}</ReactMarkdown>
          ) : (
            <p className="text-gray-400 italic">No notes yet.</p>
          )}
        </div>
      ) : (
        <textarea
          value={notesDraft}
          onChange={(e) => setNotesDraft(e.target.value)}
          rows={8}
          className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none resize-y font-mono"
          placeholder="Write markdown notes here..."
        />
      )}
    </div>
  );
}

// ---- Study Log Tab ----

interface StudyLogTabProps {
  logDate: string;
  setLogDate: (s: string) => void;
  logDuration: number;
  setLogDuration: (n: number) => void;
  logActivity: string;
  setLogActivity: (s: string) => void;
  logNotes: string;
  setLogNotes: (s: string) => void;
  logMsg: string;
  logSubmitting: boolean;
  onSubmit: (e: React.FormEvent) => void;
  logs: StudyLog[];
  logsLoading: boolean;
}

function StudyLogTab({
  logDate,
  setLogDate,
  logDuration,
  setLogDuration,
  logActivity,
  setLogActivity,
  logNotes,
  setLogNotes,
  logMsg,
  logSubmitting,
  onSubmit,
  logs,
  logsLoading,
}: StudyLogTabProps) {
  return (
    <div className="space-y-4">
      {/* Log form */}
      <form onSubmit={onSubmit} className="space-y-2">
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
              <option key={t} value={t}>
                {t}
              </option>
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
            <span
              className={`text-xs ${logMsg === "Logged" ? "text-green-600" : "text-red-600"}`}
            >
              {logMsg}
            </span>
          )}
        </div>
      </form>

      {/* Study history */}
      <div>
        <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
          History
        </h4>
        {logsLoading ? (
          <p className="text-xs text-gray-400">Loading...</p>
        ) : logs.length === 0 ? (
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
                  <p className="text-xs text-gray-500 mt-0.5 line-clamp-2 break-words">
                    {log.notes}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ---- Linked Problems Tab ----

const DIFFICULTY_COLORS: Record<string, string> = {
  easy: "text-green-600",
  medium: "text-yellow-600",
  hard: "text-red-600",
};

function LinkedProblemsTab({ nodeId }: { nodeId: number }) {
  const { data: problems, isLoading } = useQuery({
    queryKey: ["framework", "nodes", nodeId, "problems"],
    queryFn: () => api.get<Problem[]>(`/framework/nodes/${nodeId}/problems`),
  });

  if (isLoading) {
    return <p className="text-xs text-gray-400">Loading...</p>;
  }

  if (!problems || problems.length === 0) {
    return (
      <p className="text-sm text-gray-400 py-6 text-center">
        No problems linked to this topic.
      </p>
    );
  }

  return (
    <div className="space-y-1.5">
      <p className="text-xs text-gray-500 mb-2">{problems.length} linked problem{problems.length !== 1 ? "s" : ""}</p>
      {problems.map((p) => (
        <a
          key={p.id}
          href={`/problems?search=${encodeURIComponent(p.title)}`}
          className="block border border-gray-200 rounded px-3 py-2 hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-800 truncate">{p.title}</span>
            {p.difficulty && (
              <span className={`text-xs font-medium ml-2 ${DIFFICULTY_COLORS[p.difficulty] ?? "text-gray-500"}`}>
                {p.difficulty}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 mt-0.5">
            {p.pattern && <span className="text-xs text-blue-600">{p.pattern}</span>}
            {p.company_tags.length > 0 && (
              <span className="text-xs text-gray-400">{p.company_tags.slice(0, 3).join(", ")}</span>
            )}
            {p.is_completed && <span className="text-xs text-green-600">[done]</span>}
          </div>
        </a>
      ))}
    </div>
  );
}

// ---- Linked Questions Tab ----

function LinkedQuestionsTab({ nodeId }: { nodeId: number }) {
  const { data: questions, isLoading } = useQuery({
    queryKey: ["framework", "nodes", nodeId, "questions"],
    queryFn: () => api.get<InterviewQuestion[]>(`/framework/nodes/${nodeId}/questions`),
  });

  if (isLoading) {
    return <p className="text-xs text-gray-400">Loading...</p>;
  }

  if (!questions || questions.length === 0) {
    return (
      <p className="text-sm text-gray-400 py-6 text-center">
        No questions linked to this topic.
      </p>
    );
  }

  return (
    <div className="space-y-1.5">
      <p className="text-xs text-gray-500 mb-2">{questions.length} linked question{questions.length !== 1 ? "s" : ""}</p>
      {questions.map((q) => (
        <a
          key={q.id}
          href={`/questions?search=${encodeURIComponent(q.question_text.slice(0, 50))}`}
          className="block border border-gray-200 rounded px-3 py-2 hover:bg-gray-50 transition-colors"
        >
          <p className="text-sm text-gray-800 line-clamp-2">{q.question_text}</p>
          <div className="flex items-center gap-2 mt-0.5">
            {q.company && <span className="text-xs text-blue-600">{q.company}</span>}
            {q.question_type && <span className="text-xs text-gray-500">{q.question_type}</span>}
            {q.level && <span className="text-xs text-gray-400">{q.level}</span>}
            {q.is_reviewed && <span className="text-xs text-green-600">[reviewed]</span>}
          </div>
        </a>
      ))}
    </div>
  );
}
