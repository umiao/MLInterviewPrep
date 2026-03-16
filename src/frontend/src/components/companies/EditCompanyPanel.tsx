import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../utils/api";
import { useToast } from "../../contexts/ToastContext";
import type { Company, CompanyStatus } from "../../types/company";

const STATUSES: { value: CompanyStatus; label: string }[] = [
  { value: "applied", label: "Applied" },
  { value: "phone_screen", label: "Phone Screen" },
  { value: "onsite", label: "Onsite" },
  { value: "offer", label: "Offer" },
  { value: "rejected", label: "Rejected" },
];

interface EditCompanyPanelProps {
  company: Company;
  onSaved: (updated: Company) => void;
  onCancel: () => void;
}

interface EditForm {
  name: string;
  group_tag: string;
  status: CompanyStatus;
  applied_at: string;
  notes: string;
}

export default function EditCompanyPanel({
  company,
  onSaved,
  onCancel,
}: EditCompanyPanelProps) {
  const queryClient = useQueryClient();
  const toast = useToast();

  const [form, setForm] = useState<EditForm>({
    name: company.name,
    group_tag: company.group_tag ?? "",
    status: company.status,
    applied_at: company.applied_at ?? "",
    notes: company.notes ?? "",
  });

  const mutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      api.put<Company>(`/companies/${company.id}`, payload),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ["companies"] });
      toast.success("Company updated");
      onSaved(updated);
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to update company");
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) return;
    mutation.mutate({
      name: form.name.trim(),
      group_tag: form.group_tag.trim() || null,
      status: form.status,
      applied_at: form.applied_at || null,
      notes: form.notes.trim() || null,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1">
          Name *
        </label>
        <input
          type="text"
          required
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1">
          Group tag
        </label>
        <input
          type="text"
          value={form.group_tag}
          onChange={(e) => setForm({ ...form, group_tag: e.target.value })}
          placeholder="e.g. FAANG, Startup"
          className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1">
          Status
        </label>
        <select
          value={form.status}
          onChange={(e) =>
            setForm({ ...form, status: e.target.value as CompanyStatus })
          }
          className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
        >
          {STATUSES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1">
          Applied date
        </label>
        <input
          type="date"
          value={form.applied_at}
          onChange={(e) => setForm({ ...form, applied_at: e.target.value })}
          className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1">
          Notes
        </label>
        <textarea
          value={form.notes}
          onChange={(e) => setForm({ ...form, notes: e.target.value })}
          rows={3}
          className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
        />
      </div>

      <div className="flex justify-end gap-2 pt-1">
        <button
          type="button"
          onClick={onCancel}
          disabled={mutation.isPending}
          className="px-3 py-1 text-xs border border-gray-300 rounded hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={mutation.isPending || !form.name.trim()}
          className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {mutation.isPending ? "Saving..." : "Save"}
        </button>
      </div>
    </form>
  );
}
