import { useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiRequestError } from "../../utils/api";
import { useToast } from "../../contexts/ToastContext";
import ConfirmDialog from "../ui/ConfirmDialog";
import FrameworkNodePicker from "../framework/FrameworkNodePicker";
import ListenButton from "../ui/ListenButton";
import type { InterviewQuestion, QuestionAnalysis, QuestionType } from "../../types/question";
import LoadingSpinner from "../ui/LoadingSpinner";

const QUESTION_TYPES: { value: QuestionType; label: string }[] = [
  { value: "coding", label: "Coding" },
  { value: "ml_theory", label: "ML Theory" },
  { value: "ml_system_design", label: "ML System Design" },
  { value: "behavioral", label: "Behavioral" },
  { value: "ml_coding", label: "ML Coding" },
  { value: "general_system_design", label: "System Design" },
];

interface EditFormData {
  company: string;
  role: string;
  question_type: QuestionType | "";
  level: string;
  year: string;
  tags: string;
  difficulty_estimate: string;
  mapped_framework_node_id: number | null;
}

function questionToForm(q: InterviewQuestion): EditFormData {
  return {
    company: q.company ?? "",
    role: q.role ?? "",
    question_type: q.question_type ?? "",
    level: q.level ?? "",
    year: q.year?.toString() ?? "",
    tags: q.tags.join(", "),
    difficulty_estimate: q.difficulty_estimate ?? "",
    mapped_framework_node_id: q.mapped_framework_node_id,
  };
}

function formToPayload(form: EditFormData): Record<string, unknown> {
  const payload: Record<string, unknown> = {};
  payload.company = form.company.trim() || null;
  payload.role = form.role.trim() || null;
  payload.question_type = form.question_type || null;
  payload.level = form.level.trim() || null;
  payload.difficulty_estimate = form.difficulty_estimate.trim() || null;
  payload.mapped_framework_node_id = form.mapped_framework_node_id;

  if (form.year.trim()) {
    const y = parseInt(form.year.trim(), 10);
    payload.year = isNaN(y) ? null : y;
  } else {
    payload.year = null;
  }

  if (form.tags.trim()) {
    payload.tags = form.tags
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
  } else {
    payload.tags = [];
  }

  return payload;
}

/* ---------- Analysis Panel ---------- */

function AnalysisPanel({
  analysis,
  loading,
}: {
  analysis: QuestionAnalysis | null;
  loading: boolean;
}) {
  if (loading) {
    return <LoadingSpinner message="Analyzing with LLM..." size="sm" />;
  }
  if (!analysis) return null;

  return (
    <div className="space-y-3 mt-3 p-3 bg-blue-50 rounded border border-blue-100">
      <div>
        <h4 className="text-xs font-semibold text-gray-500 uppercase">
          Solution Approach
        </h4>
        <p className="text-sm text-gray-700 mt-1 break-words">{analysis.solution_approach}</p>
      </div>
      {analysis.key_concepts.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase">
            Key Concepts
          </h4>
          <div className="flex flex-wrap gap-1 mt-1">
            {analysis.key_concepts.map((c) => (
              <span
                key={c}
                className="text-xs px-2 py-0.5 rounded bg-white border border-blue-200 text-blue-700"
              >
                {c}
              </span>
            ))}
          </div>
        </div>
      )}
      <div className="flex gap-6">
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase">
            Difficulty
          </h4>
          <span className="text-sm font-medium capitalize">
            {analysis.difficulty}
          </span>
        </div>
        {analysis.related_patterns.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase">
              Related Patterns
            </h4>
            <span className="text-sm text-gray-700">
              {analysis.related_patterns.join(", ")}
            </span>
          </div>
        )}
      </div>
      {analysis.suggested_study && (
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase">
            Suggested Study
          </h4>
          <p className="text-sm text-gray-700 mt-1">
            {analysis.suggested_study}
          </p>
        </div>
      )}
    </div>
  );
}

/* ---------- EditableQuestionRow ---------- */

interface EditableQuestionRowProps {
  question: InterviewQuestion;
  onToggleReviewed: (id: number, reviewed: boolean) => void;
}

export default function EditableQuestionRow({
  question,
  onToggleReviewed,
}: EditableQuestionRowProps) {
  const queryClient = useQueryClient();
  const toast = useToast();

  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<EditFormData>(questionToForm(question));
  const [deleteOpen, setDeleteOpen] = useState(false);

  // LLM analysis state
  const [analysis, setAnalysis] = useState<QuestionAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);

  // Sync form when question changes from outside
  useEffect(() => {
    if (!editing) {
      setForm(questionToForm(question));
    }
  }, [question, editing]);

  // Try to parse existing notes as analysis
  useEffect(() => {
    if (question.notes) {
      try {
        const parsed = JSON.parse(question.notes) as QuestionAnalysis;
        if (parsed.solution_approach) {
          setAnalysis(parsed);
        }
      } catch {
        // notes is plain text, not analysis JSON
      }
    }
  }, [question.notes]);

  const updateMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      api.put(`/questions/${question.id}`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["questions"] });
      toast.success("Question updated");
      setEditing(false);
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to update question");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => api.del(`/questions/${question.id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["questions"] });
      toast.success("Question deleted");
      setDeleteOpen(false);
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to delete question");
    },
  });

  function handleSave() {
    updateMutation.mutate(formToPayload(form));
  }

  function handleCancel() {
    setForm(questionToForm(question));
    setEditing(false);
  }

  async function handleAnalyze() {
    setAnalyzing(true);
    setAnalyzeError(null);
    try {
      const result = await api.post<QuestionAnalysis>(
        `/questions/${question.id}/analyze`,
      );
      setAnalysis(result);
      queryClient.invalidateQueries({ queryKey: ["questions"] });
    } catch (err) {
      const msg =
        err instanceof ApiRequestError ? err.message : String(err);
      setAnalyzeError(msg);
    } finally {
      setAnalyzing(false);
    }
  }

  const inputClass =
    "w-full text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-300";

  return (
    <tr>
      <td colSpan={8} className="px-4 py-3 bg-gray-50 border-b border-gray-200">
        <div className="space-y-3">
          {/* Full question text */}
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">
              Question
            </h4>
            <p className="text-sm text-gray-800 whitespace-pre-wrap break-words">
              {question.question_text}
            </p>
          </div>

          {editing ? (
            /* ---------- Edit mode ---------- */
            <div className="space-y-3 p-3 bg-white rounded border border-gray-200">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    Company
                  </label>
                  <input
                    type="text"
                    value={form.company}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, company: e.target.value }))
                    }
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    Role
                  </label>
                  <input
                    type="text"
                    value={form.role}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, role: e.target.value }))
                    }
                    className={inputClass}
                  />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    Type
                  </label>
                  <select
                    value={form.question_type}
                    onChange={(e) =>
                      setForm((f) => ({
                        ...f,
                        question_type: e.target.value as QuestionType | "",
                      }))
                    }
                    className={inputClass}
                  >
                    <option value="">-- None --</option>
                    {QUESTION_TYPES.map((t) => (
                      <option key={t.value} value={t.value}>
                        {t.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    Level
                  </label>
                  <input
                    type="text"
                    value={form.level}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, level: e.target.value }))
                    }
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    Year
                  </label>
                  <input
                    type="text"
                    value={form.year}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, year: e.target.value }))
                    }
                    className={inputClass}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={form.tags}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, tags: e.target.value }))
                    }
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    Difficulty
                  </label>
                  <input
                    type="text"
                    value={form.difficulty_estimate}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, difficulty_estimate: e.target.value }))
                    }
                    className={inputClass}
                    placeholder="e.g. easy, medium, hard"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">
                  Framework Topic
                </label>
                <FrameworkNodePicker
                  value={form.mapped_framework_node_id}
                  onChange={(id) =>
                    setForm((f) => ({ ...f, mapped_framework_node_id: id }))
                  }
                  placeholder="Link to a framework topic..."
                />
              </div>
              <div className="flex items-center gap-2 pt-2">
                <button
                  onClick={handleSave}
                  disabled={updateMutation.isPending}
                  className="text-xs px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {updateMutation.isPending ? "Saving..." : "Save"}
                </button>
                <button
                  onClick={handleCancel}
                  disabled={updateMutation.isPending}
                  className="text-xs px-3 py-1.5 rounded border border-gray-300 text-gray-600 hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            /* ---------- View mode metadata ---------- */
            <div className="flex flex-wrap gap-4 text-xs text-gray-500">
              {question.level && <span>Level: {question.level}</span>}
              {question.interview_round && (
                <span>Round: {question.interview_round}</span>
              )}
              {question.year && <span>Year: {question.year}</span>}
              {question.tags.length > 0 && (
                <span>Tags: {question.tags.join(", ")}</span>
              )}
              {question.difficulty_estimate && (
                <span>Difficulty: {question.difficulty_estimate}</span>
              )}
              {question.mapped_framework_node_id && (
                <span>Framework node: #{question.mapped_framework_node_id}</span>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-3">
            <ListenButton
              contentType="interview_question"
              contentId={question.id}
              title={question.question_text.slice(0, 80)}
            />
            <button
              onClick={() =>
                onToggleReviewed(question.id, !question.is_reviewed)
              }
              className={`text-xs px-3 py-1.5 rounded border ${
                question.is_reviewed
                  ? "bg-green-50 border-green-300 text-green-700"
                  : "bg-white border-gray-300 text-gray-600 hover:bg-gray-50"
              }`}
            >
              {question.is_reviewed ? "[x] Reviewed" : "[ ] Mark Reviewed"}
            </button>
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="text-xs px-3 py-1.5 rounded border bg-white border-blue-300 text-blue-700 hover:bg-blue-50 disabled:opacity-50"
            >
              {analyzing ? "Analyzing..." : analysis ? "Re-analyze" : "Analyze"}
            </button>
            {!editing && (
              <button
                onClick={() => setEditing(true)}
                className="text-xs px-3 py-1.5 rounded border bg-white border-gray-300 text-gray-600 hover:bg-gray-50"
              >
                Edit
              </button>
            )}
            <button
              onClick={() => setDeleteOpen(true)}
              className="text-xs px-3 py-1.5 rounded border border-red-300 text-red-600 hover:bg-red-50"
            >
              Delete
            </button>
          </div>

          {/* Analysis error */}
          {analyzeError && (
            <div className="text-xs text-red-600 bg-red-50 px-3 py-2 rounded">
              {analyzeError}
            </div>
          )}

          {/* Analysis results */}
          <AnalysisPanel analysis={analysis} loading={analyzing} />
        </div>

        {/* Delete confirm */}
        <ConfirmDialog
          open={deleteOpen}
          onClose={() => setDeleteOpen(false)}
          onConfirm={() => deleteMutation.mutate()}
          title="Delete Question"
          message={`Delete this question? "${question.question_text.slice(0, 80)}${question.question_text.length > 80 ? "..." : ""}"`}
          confirmLabel="Delete"
          confirmVariant="danger"
          loading={deleteMutation.isPending}
        />
      </td>
    </tr>
  );
}
