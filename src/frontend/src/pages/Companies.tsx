import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiRequestError } from "../utils/api";
import { useToast } from "../contexts/ToastContext";
import type {
  Company,
  CompanyCreate,
  CompanyStatus,
  FocusTopic,
} from "../types/company";

const STATUSES: { value: CompanyStatus; label: string; color: string }[] = [
  { value: "applied", label: "Applied", color: "bg-gray-100 border-gray-300" },
  {
    value: "phone_screen",
    label: "Phone Screen",
    color: "bg-blue-50 border-blue-300",
  },
  {
    value: "onsite",
    label: "Onsite",
    color: "bg-yellow-50 border-yellow-300",
  },
  { value: "offer", label: "Offer", color: "bg-green-50 border-green-300" },
  {
    value: "rejected",
    label: "Rejected",
    color: "bg-red-50 border-red-300",
  },
];


function ProgressBar({ pct }: { pct: number }) {
  return (
    <div className="w-full bg-gray-200 rounded-full h-1.5">
      <div
        className="bg-blue-500 h-1.5 rounded-full"
        style={{ width: `${Math.min(100, pct)}%` }}
      />
    </div>
  );
}

/* ---------- Add Company Modal ---------- */

function AddCompanyModal({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: () => void;
}) {
  const [form, setForm] = useState<CompanyCreate>({
    name: "",
    group_tag: null,
    status: "applied",
    applied_at: new Date().toISOString().slice(0, 10),
    notes: null,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await api.post("/companies", {
        ...form,
        name: form.name.trim(),
        group_tag: form.group_tag?.trim() || null,
        notes: form.notes?.trim() || null,
      });
      onCreated();
    } catch (err) {
      const msg =
        err instanceof ApiRequestError ? err.message : String(err);
      setError(msg);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-lg shadow-xl w-full max-w-md p-6 space-y-4"
      >
        <h2 className="text-lg font-semibold">Add Company</h2>

        {error && (
          <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Company name *
          </label>
          <input
            type="text"
            required
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            autoFocus
          />
        </div>

        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Group tag
            </label>
            <input
              type="text"
              value={form.group_tag ?? ""}
              onChange={(e) =>
                setForm({ ...form, group_tag: e.target.value || null })
              }
              placeholder="e.g. FAANG, Startup"
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={form.status}
              onChange={(e) =>
                setForm({
                  ...form,
                  status: e.target.value as CompanyStatus,
                })
              }
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            >
              {STATUSES.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Applied date
          </label>
          <input
            type="date"
            value={form.applied_at ?? ""}
            onChange={(e) =>
              setForm({ ...form, applied_at: e.target.value || null })
            }
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <textarea
            value={form.notes ?? ""}
            onChange={(e) =>
              setForm({ ...form, notes: e.target.value || null })
            }
            rows={3}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
          />
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving || !form.name.trim()}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Add Company"}
          </button>
        </div>
      </form>
    </div>
  );
}

/* ---------- Focus Topics Panel ---------- */

function FocusTopicsPanel({
  company,
  onClose,
  onStatusChange,
}: {
  company: Company;
  onClose: () => void;
  onStatusChange: (newStatus: CompanyStatus) => void;
}) {
  const queryClient = useQueryClient();
  const toast = useToast();
  const { data: topics = [], isLoading: loading } = useQuery({
    queryKey: ["companies", company.id, "focus"],
    queryFn: () => api.get<FocusTopic[]>(`/companies/${company.id}/focus`),
  });
  const [status, setStatus] = useState<CompanyStatus>(company.status);

  const statusMutation = useMutation({
    mutationFn: (newStatus: CompanyStatus) =>
      api.put(`/companies/${company.id}`, { status: newStatus }),
    onSuccess: (_data, newStatus) => {
      onStatusChange(newStatus);
      queryClient.invalidateQueries({ queryKey: ["companies"] });
      toast.success("Status updated");
    },
    onError: () => {
      setStatus(company.status);
      toast.error("Failed to update status");
    },
  });

  function handleStatusSave() {
    if (status === company.status) return;
    statusMutation.mutate(status);
  }

  const saving = statusMutation.isPending;

  return (
    <div className="fixed inset-y-0 right-0 w-80 bg-white border-l border-gray-200 shadow-lg z-40 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <h2 className="text-lg font-semibold truncate" title={company.name}>
          {company.name}
        </h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-xl leading-none"
        >
          x
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        {/* Company info */}
        <div className="space-y-2">
          {company.group_tag && (
            <div className="text-xs text-gray-500">
              Group: <span className="font-medium">{company.group_tag}</span>
            </div>
          )}
          {company.applied_at && (
            <div className="text-xs text-gray-500">
              Applied: {company.applied_at}
            </div>
          )}
          {company.notes && (
            <p className="text-sm text-gray-600">{company.notes}</p>
          )}
        </div>

        {/* Status changer */}
        <div className="space-y-1">
          <label className="text-xs font-medium text-gray-500">Status</label>
          <div className="flex gap-2">
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as CompanyStatus)}
              className="flex-1 text-sm border border-gray-300 rounded px-2 py-1"
            >
              {STATUSES.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
            {status !== company.status && (
              <button
                onClick={handleStatusSave}
                disabled={saving}
                className="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? "..." : "Save"}
              </button>
            )}
          </div>
        </div>

        {/* Focus topics */}
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-gray-700">
            Focus Topics
          </h3>
          <p className="text-xs text-gray-400">
            Topics to study for this company (progress &lt; 80%)
          </p>

          {loading && (
            <div className="text-sm text-gray-400 py-4 text-center">
              Loading...
            </div>
          )}

          {!loading && topics.length === 0 && (
            <div className="text-sm text-gray-400 py-4 text-center">
              No focus topics. Add topic weights to this company or all topics
              are above 80%.
            </div>
          )}

          {!loading &&
            topics.map((t) => (
              <div
                key={t.node_id}
                className="border border-gray-200 rounded p-2 space-y-1"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium truncate">
                    {t.title}
                  </span>
                  <span className="text-xs text-gray-400 shrink-0 ml-2">
                    w:{t.weight}
                  </span>
                </div>
                <ProgressBar pct={t.progress_pct} />
                <div className="flex justify-between text-xs text-gray-400">
                  <span>{t.progress_pct.toFixed(0)}% done</span>
                  <span>conf: {t.confidence}/5</span>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

/* ---------- Company Card ---------- */

function CompanyCard({
  company,
  onClick,
}: {
  company: Company;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="w-full text-left bg-white border border-gray-200 rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow space-y-1.5"
    >
      <div className="flex items-start justify-between gap-2">
        <span className="font-medium text-sm truncate">{company.name}</span>
        {company.group_tag && (
          <span className="text-xs px-1.5 py-0.5 rounded bg-purple-100 text-purple-700 shrink-0">
            {company.group_tag}
          </span>
        )}
      </div>
      {company.applied_at && (
        <div className="text-xs text-gray-400">{company.applied_at}</div>
      )}
      {company.notes && (
        <p className="text-xs text-gray-500 line-clamp-2">{company.notes}</p>
      )}
    </button>
  );
}

/* ---------- Kanban Column ---------- */

function KanbanColumn({
  status,
  label,
  colorClass,
  companies,
  onCardClick,
}: {
  status: CompanyStatus;
  label: string;
  colorClass: string;
  companies: Company[];
  onCardClick: (c: Company) => void;
}) {
  return (
    <div
      className={`flex flex-col w-64 shrink-0 border rounded-lg ${colorClass}`}
    >
      <div className="flex items-center justify-between px-3 py-2 border-b border-inherit">
        <h3 className="text-sm font-semibold">{label}</h3>
        <span className="text-xs text-gray-500 bg-white/70 rounded-full px-2 py-0.5">
          {companies.length}
        </span>
      </div>
      <div
        className="flex-1 p-2 space-y-2 overflow-y-auto"
        data-status={status}
        style={{ minHeight: "12rem" }}
      >
        {companies.map((c) => (
          <CompanyCard key={c.id} company={c} onClick={() => onCardClick(c)} />
        ))}
        {companies.length === 0 && (
          <div className="text-xs text-gray-400 text-center py-6">
            No companies
          </div>
        )}
      </div>
    </div>
  );
}

/* ---------- Main Page ---------- */

export default function Companies() {
  const queryClient = useQueryClient();
  const { data: companies = [], isLoading: loading, error: queryError } = useQuery({
    queryKey: ["companies"],
    queryFn: () => api.get<Company[]>("/companies"),
  });
  const error = queryError ? queryError.message : null;
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);

  // Group companies by status
  const byStatus: Record<CompanyStatus, Company[]> = {
    applied: [],
    phone_screen: [],
    onsite: [],
    offer: [],
    rejected: [],
  };
  for (const c of companies) {
    const bucket = byStatus[c.status as CompanyStatus];
    if (bucket) {
      bucket.push(c);
    } else {
      byStatus.applied.push(c);
    }
  }

  function handleStatusChange(companyId: number, newStatus: CompanyStatus) {
    queryClient.invalidateQueries({ queryKey: ["companies"] });
    if (selectedCompany?.id === companyId) {
      setSelectedCompany((prev) =>
        prev ? { ...prev, status: newStatus } : null,
      );
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold">Companies</h1>
          <p className="text-sm text-gray-500">
            {companies.length} company{companies.length !== 1 ? "ies" : ""}
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + Add Company
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 text-red-700 px-4 py-2 rounded mb-3">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-gray-500 py-8 text-center">Loading...</div>
      )}

      {/* Kanban Board */}
      {!loading && (
        <div className="flex gap-4 overflow-x-auto pb-4 flex-1 min-h-0">
          {STATUSES.map((s) => (
            <KanbanColumn
              key={s.value}
              status={s.value}
              label={s.label}
              colorClass={s.color}
              companies={byStatus[s.value]}
              onCardClick={setSelectedCompany}
            />
          ))}
        </div>
      )}

      {/* Add Company Modal */}
      {showAddModal && (
        <AddCompanyModal
          onClose={() => setShowAddModal(false)}
          onCreated={() => {
            setShowAddModal(false);
            queryClient.invalidateQueries({ queryKey: ["companies"] });
          }}
        />
      )}

      {/* Focus Topics Panel */}
      {selectedCompany && (
        <FocusTopicsPanel
          company={selectedCompany}
          onClose={() => setSelectedCompany(null)}
          onStatusChange={(newStatus) =>
            handleStatusChange(selectedCompany.id, newStatus)
          }
        />
      )}
    </div>
  );
}
