import { useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../utils/api";
import { useToast } from "../../contexts/ToastContext";
import Modal from "../ui/Modal";
import ProblemFormFields, { formToPayload } from "./ProblemFormFields";
import type { ProblemFormData } from "./ProblemFormFields";
import type { Problem } from "../../types/problem";

interface EditProblemModalProps {
  problem: Problem | null;
  onClose: () => void;
}

function problemToForm(p: Problem): ProblemFormData {
  return {
    title: p.title,
    leetcode_id: p.leetcode_id != null ? String(p.leetcode_id) : "",
    url: p.url ?? "",
    difficulty: p.difficulty ?? "",
    tags: p.tags.join(", "),
    pattern: p.pattern ?? "",
    category: p.category,
    source: p.source ?? "",
    company_tags: p.company_tags.join(", "),
    priority: p.priority,
    framework_node_id: p.framework_node_id,
    description: p.description ?? "",
    neetcode_slug: p.neetcode_slug ?? "",
  };
}

export default function EditProblemModal({
  problem,
  onClose,
}: EditProblemModalProps) {
  const queryClient = useQueryClient();
  const toast = useToast();
  const [form, setForm] = useState<ProblemFormData | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when problem changes
  useEffect(() => {
    if (problem) {
      setForm(problemToForm(problem));
      setErrors({});
    } else {
      setForm(null);
    }
  }, [problem]);

  const mutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      api.put<Problem>(`/problems/${problem!.id}`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["problems"] });
      toast.success("Problem updated");
      onClose();
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to update problem");
    },
  });

  function handleChange(updates: Partial<ProblemFormData>) {
    setForm((prev) => (prev ? { ...prev, ...updates } : prev));
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
    if (!form) return;
    const newErrors: Record<string, string> = {};
    if (!form.title.trim()) newErrors.title = "Title is required";
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    mutation.mutate(formToPayload(form));
  }

  if (!problem || !form) return null;

  return (
    <Modal open={true} onClose={onClose} title="Edit Problem" width="max-w-xl">
      <form onSubmit={handleSubmit}>
        <ProblemFormFields form={form} onChange={handleChange} errors={errors} />
        <div className="flex justify-end gap-2 mt-4 pt-3 border-t border-gray-100">
          <button
            type="button"
            onClick={onClose}
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
            {mutation.isPending ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
