import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../utils/api";
import { useToast } from "../../contexts/ToastContext";
import Modal from "../ui/Modal";
import FormField from "../ui/FormField";
import FrameworkNodePicker from "../framework/FrameworkNodePicker";
import type { QuestionType, InterviewQuestion } from "../../types/question";

const QUESTION_TYPES: { value: QuestionType; label: string }[] = [
  { value: "coding", label: "Coding" },
  { value: "ml_theory", label: "ML Theory" },
  { value: "ml_system_design", label: "ML System Design" },
  { value: "behavioral", label: "Behavioral" },
  { value: "ml_coding", label: "ML Coding" },
  { value: "general_system_design", label: "System Design" },
];

interface QuestionFormData {
  question_text: string;
  company: string;
  role: string;
  question_type: QuestionType | "";
  level: string;
  year: string;
  tags: string;
  mapped_framework_node_id: number | null;
}

const EMPTY_FORM: QuestionFormData = {
  question_text: "",
  company: "",
  role: "",
  question_type: "",
  level: "",
  year: "",
  tags: "",
  mapped_framework_node_id: null,
};

function formToPayload(form: QuestionFormData): Record<string, unknown> {
  const payload: Record<string, unknown> = {
    question_text: form.question_text.trim(),
  };
  if (form.company.trim()) payload.company = form.company.trim();
  if (form.role.trim()) payload.role = form.role.trim();
  if (form.question_type) payload.question_type = form.question_type;
  if (form.level.trim()) payload.level = form.level.trim();
  if (form.year.trim()) {
    const y = parseInt(form.year.trim(), 10);
    if (!isNaN(y)) payload.year = y;
  }
  if (form.tags.trim()) {
    payload.tags = form.tags
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
  }
  if (form.mapped_framework_node_id !== null) {
    payload.mapped_framework_node_id = form.mapped_framework_node_id;
  }
  return payload;
}

interface AddQuestionModalProps {
  open: boolean;
  onClose: () => void;
}

export default function AddQuestionModal({ open, onClose }: AddQuestionModalProps) {
  const queryClient = useQueryClient();
  const toast = useToast();
  const [form, setForm] = useState<QuestionFormData>({ ...EMPTY_FORM });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const mutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      api.post<InterviewQuestion>("/questions", payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["questions"] });
      toast.success("Question created");
      setForm({ ...EMPTY_FORM });
      setErrors({});
      onClose();
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to create question");
    },
  });

  function handleChange(updates: Partial<QuestionFormData>) {
    setForm((prev) => ({ ...prev, ...updates }));
    const cleared: Record<string, string> = {};
    for (const key of Object.keys(updates)) {
      if (errors[key]) cleared[key] = "";
    }
    if (Object.keys(cleared).length > 0) {
      setErrors((prev) => ({ ...prev, ...cleared }));
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const newErrors: Record<string, string> = {};
    if (!form.question_text.trim()) newErrors.question_text = "Question text is required";
    if (form.year.trim()) {
      const y = parseInt(form.year.trim(), 10);
      if (isNaN(y) || y < 1900 || y > 2100) newErrors.year = "Invalid year";
    }
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    mutation.mutate(formToPayload(form));
  }

  function handleClose() {
    if (!mutation.isPending) {
      setForm({ ...EMPTY_FORM });
      setErrors({});
      onClose();
    }
  }

  const inputClass =
    "w-full text-sm border border-gray-300 rounded px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-300";

  return (
    <Modal open={open} onClose={handleClose} title="Add Question" width="max-w-xl">
      <form onSubmit={handleSubmit}>
        <FormField label="Question Text" htmlFor="q-text" required error={errors.question_text}>
          <textarea
            id="q-text"
            value={form.question_text}
            onChange={(e) => handleChange({ question_text: e.target.value })}
            rows={3}
            className={inputClass + " resize-y"}
            placeholder="Enter the interview question..."
          />
        </FormField>

        <div className="grid grid-cols-2 gap-3">
          <FormField label="Company" htmlFor="q-company">
            <input
              id="q-company"
              type="text"
              value={form.company}
              onChange={(e) => handleChange({ company: e.target.value })}
              className={inputClass}
              placeholder="e.g. Google"
            />
          </FormField>
          <FormField label="Role" htmlFor="q-role">
            <input
              id="q-role"
              type="text"
              value={form.role}
              onChange={(e) => handleChange({ role: e.target.value })}
              className={inputClass}
              placeholder="e.g. MLE"
            />
          </FormField>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <FormField label="Type" htmlFor="q-type">
            <select
              id="q-type"
              value={form.question_type}
              onChange={(e) =>
                handleChange({ question_type: e.target.value as QuestionType | "" })
              }
              className={inputClass}
            >
              <option value="">-- Select --</option>
              {QUESTION_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </FormField>
          <FormField label="Level" htmlFor="q-level">
            <input
              id="q-level"
              type="text"
              value={form.level}
              onChange={(e) => handleChange({ level: e.target.value })}
              className={inputClass}
              placeholder="e.g. L5, Senior"
            />
          </FormField>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <FormField label="Year" htmlFor="q-year" error={errors.year}>
            <input
              id="q-year"
              type="text"
              value={form.year}
              onChange={(e) => handleChange({ year: e.target.value })}
              className={inputClass}
              placeholder="e.g. 2025"
            />
          </FormField>
          <FormField label="Tags (comma-separated)" htmlFor="q-tags">
            <input
              id="q-tags"
              type="text"
              value={form.tags}
              onChange={(e) => handleChange({ tags: e.target.value })}
              className={inputClass}
              placeholder="e.g. arrays, dp, graphs"
            />
          </FormField>
        </div>

        <FormField label="Framework Topic">
          <FrameworkNodePicker
            value={form.mapped_framework_node_id}
            onChange={(id) => handleChange({ mapped_framework_node_id: id })}
            placeholder="Link to a framework topic..."
          />
        </FormField>

        <div className="flex justify-end gap-2 mt-4 pt-3 border-t border-gray-100">
          <button
            type="button"
            onClick={handleClose}
            disabled={mutation.isPending}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {mutation.isPending ? "Creating..." : "Add Question"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
