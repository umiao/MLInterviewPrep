import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../utils/api";
import { useToast } from "../../contexts/ToastContext";
import Modal from "../ui/Modal";
import ProblemFormFields, {
  EMPTY_FORM,
  formToPayload,
} from "./ProblemFormFields";
import type { ProblemFormData } from "./ProblemFormFields";
import type { Problem } from "../../types/problem";

interface AddProblemModalProps {
  open: boolean;
  onClose: () => void;
}

export default function AddProblemModal({ open, onClose }: AddProblemModalProps) {
  const queryClient = useQueryClient();
  const toast = useToast();
  const [form, setForm] = useState<ProblemFormData>({ ...EMPTY_FORM });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const mutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      api.post<Problem>("/problems", payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["problems"] });
      toast.success("Problem created");
      setForm({ ...EMPTY_FORM });
      setErrors({});
      onClose();
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to create problem");
    },
  });

  function handleChange(updates: Partial<ProblemFormData>) {
    setForm((prev) => ({ ...prev, ...updates }));
    // Clear field errors on change
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
    if (!form.title.trim()) newErrors.title = "Title is required";
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

  return (
    <Modal open={open} onClose={handleClose} title="Add Problem" width="max-w-xl">
      <form onSubmit={handleSubmit}>
        <ProblemFormFields form={form} onChange={handleChange} errors={errors} />
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
            {mutation.isPending ? "Creating..." : "Add Problem"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
