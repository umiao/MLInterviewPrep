import { useEffect, useRef, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiRequestError } from "../utils/api";
import { useToast } from "../contexts/ToastContext";
import LoadingSpinner from "../components/ui/LoadingSpinner";

/* ================================================================
   Type definitions
   ================================================================ */

interface ImportResult {
  inserted: number;
  skipped: number;
  errors: number;
}

interface FullImportResult {
  problems: ImportResult;
  framework_nodes: ImportResult;
  companies: ImportResult;
  interview_questions: ImportResult;
}

interface CsvImportResult {
  inserted: number;
  skipped: number;
  errors: number;
}

interface SeedURL {
  id: number;
  url: string;
  source_site: string;
  company: string | null;
  role_filter: string | null;
  is_active: boolean;
  last_checked_at: string | null;
  check_interval_hours: number;
}

interface ScraperJob {
  job_id: string;
  status: string;
  seeds_total: number;
  seeds_processed: number;
  questions_found: number;
  started_at: string;
  completed_at: string | null;
  errors: string[];
}

const SOURCE_SITES = ["blind", "1point3acres", "leetcode_discuss", "glassdoor"] as const;

/* ================================================================
   Export Panel
   ================================================================ */

function ExportPanel() {
  const toast = useToast();
  const [exporting, setExporting] = useState(false);

  async function handleExportJson() {
    setExporting(true);
    try {
      const data = await api.get("/export");
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `mlprep-export-${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success("JSON export downloaded");
    } catch (err) {
      const msg =
        err instanceof ApiRequestError ? err.message : "Export failed";
      toast.error(msg);
    } finally {
      setExporting(false);
    }
  }

  async function handleExportCsv() {
    setExporting(true);
    try {
      const data = await api.get<{
        problems: Array<Record<string, unknown>>;
      }>("/export");
      const problems = data.problems ?? [];
      if (problems.length === 0) {
        toast.info("No problems to export");
        setExporting(false);
        return;
      }
      const headers = [
        "leetcode_id",
        "title",
        "url",
        "difficulty",
        "pattern",
        "category",
        "source",
        "priority",
        "tags",
        "company_tags",
      ];
      const csvRows = [headers.join(",")];
      for (const p of problems) {
        const row = headers.map((h) => {
          const val = p[h];
          if (Array.isArray(val)) return `"${val.join(";")}"`;
          if (val == null) return "";
          const str = String(val);
          return str.includes(",") || str.includes('"')
            ? `"${str.replace(/"/g, '""')}"`
            : str;
        });
        csvRows.push(row.join(","));
      }
      const blob = new Blob([csvRows.join("\n")], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `mlprep-problems-${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success("CSV export downloaded");
    } catch (err) {
      const msg =
        err instanceof ApiRequestError ? err.message : "CSV export failed";
      toast.error(msg);
    } finally {
      setExporting(false);
    }
  }

  return (
    <section className="bg-white rounded-lg border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-1">Export Data</h2>
      <p className="text-sm text-gray-500 mb-4">
        Download all your data as JSON (full backup) or CSV (problems only).
      </p>
      <div className="flex gap-3">
        <button
          onClick={handleExportJson}
          disabled={exporting}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm"
        >
          {exporting ? "Exporting..." : "Download JSON"}
        </button>
        <button
          onClick={handleExportCsv}
          disabled={exporting}
          className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50 text-sm"
        >
          {exporting ? "Exporting..." : "Download CSV (Problems)"}
        </button>
      </div>
    </section>
  );
}

/* ================================================================
   Import Panel
   ================================================================ */

function ImportPanel() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const csvInputRef = useRef<HTMLInputElement>(null);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<FullImportResult | null>(
    null,
  );
  const [csvResult, setCsvResult] = useState<CsvImportResult | null>(null);

  async function handleJsonUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImporting(true);
    setImportResult(null);
    try {
      const text = await file.text();
      const payload = JSON.parse(text);
      const result = await api.post<FullImportResult>("/import", payload);
      setImportResult(result);
      queryClient.invalidateQueries();
      toast.success("JSON import complete");
    } catch (err) {
      const msg =
        err instanceof ApiRequestError
          ? err.message
          : err instanceof SyntaxError
            ? "Invalid JSON file"
            : "Import failed";
      toast.error(msg);
    } finally {
      setImporting(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleCsvUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImporting(true);
    setCsvResult(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/import/csv", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => null);
        throw new Error(
          (detail as Record<string, string>)?.detail ?? res.statusText,
        );
      }
      const result: CsvImportResult = await res.json();
      setCsvResult(result);
      queryClient.invalidateQueries();
      toast.success("CSV import complete");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "CSV import failed");
    } finally {
      setImporting(false);
      if (csvInputRef.current) csvInputRef.current.value = "";
    }
  }

  return (
    <section className="bg-white rounded-lg border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-1">Import Data</h2>
      <p className="text-sm text-gray-500 mb-4">
        Upload a JSON backup or CSV file of problems to merge into your data.
      </p>
      <div className="flex gap-3 items-center flex-wrap">
        <label className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm cursor-pointer inline-block">
          {importing ? "Importing..." : "Upload JSON"}
          <input
            ref={fileInputRef}
            type="file"
            accept=".json"
            onChange={handleJsonUpload}
            disabled={importing}
            className="hidden"
          />
        </label>
        <label className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm cursor-pointer inline-block">
          {importing ? "Importing..." : "Upload CSV"}
          <input
            ref={csvInputRef}
            type="file"
            accept=".csv"
            onChange={handleCsvUpload}
            disabled={importing}
            className="hidden"
          />
        </label>
      </div>
      {importResult && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded text-sm">
          <p className="font-medium text-green-800 mb-1">
            JSON Import Results:
          </p>
          {(
            ["problems", "framework_nodes", "companies", "interview_questions"] as const
          ).map((key) => {
            const r = importResult[key];
            return (
              <p key={key} className="text-green-700">
                {key}: {r.inserted} inserted, {r.skipped} skipped, {r.errors}{" "}
                errors
              </p>
            );
          })}
        </div>
      )}
      {csvResult && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded text-sm">
          <p className="font-medium text-green-800 mb-1">
            CSV Import Results:
          </p>
          <p className="text-green-700">
            {csvResult.inserted} inserted, {csvResult.skipped} skipped,{" "}
            {csvResult.errors} errors
          </p>
        </div>
      )}
    </section>
  );
}

/* ================================================================
   Seed Data Panel
   ================================================================ */

function SeedDataPanel() {
  const toast = useToast();
  const queryClient = useQueryClient();

  const seedMutation = useMutation({
    mutationFn: () => api.post("/import/seed"),
    onSuccess: () => {
      queryClient.invalidateQueries();
      toast.success("Seed data loaded successfully");
    },
    onError: (err: Error) => {
      toast.error(
        err instanceof ApiRequestError ? err.message : "Seed load failed",
      );
    },
  });

  return (
    <section className="bg-white rounded-lg border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-1">
        Seed Data
      </h2>
      <p className="text-sm text-gray-500 mb-4">
        Load built-in seed data (framework nodes, sample problems). Duplicates
        are automatically skipped.
      </p>
      <button
        onClick={() => seedMutation.mutate()}
        disabled={seedMutation.isPending}
        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 text-sm"
      >
        {seedMutation.isPending ? "Loading..." : "Load Seed Data"}
      </button>
    </section>
  );
}

/* ================================================================
   Add Seed URL Modal
   ================================================================ */

function AddSeedModal({
  open,
  onClose,
  onSuccess,
}: {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const toast = useToast();
  const [url, setUrl] = useState("");
  const [sourceSite, setSourceSite] = useState<string>(SOURCE_SITES[0]);
  const [company, setCompany] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [intervalHours, setIntervalHours] = useState(24);
  const [submitting, setSubmitting] = useState(false);

  function reset() {
    setUrl("");
    setSourceSite(SOURCE_SITES[0]);
    setCompany("");
    setRoleFilter("");
    setIntervalHours(24);
    setSubmitting(false);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!url.trim()) return;
    setSubmitting(true);
    try {
      await api.post("/scraper/seeds", {
        url: url.trim(),
        source_site: sourceSite,
        company: company.trim() || null,
        role_filter: roleFilter.trim() || null,
        check_interval_hours: intervalHours,
      });
      toast.success("Seed URL added");
      reset();
      onSuccess();
      onClose();
    } catch (err) {
      toast.error(
        err instanceof ApiRequestError ? err.message : "Failed to add seed URL",
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-md p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          Add Seed URL
        </h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              URL *
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="https://..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Source Site *
            </label>
            <select
              value={sourceSite}
              onChange={(e) => setSourceSite(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              {SOURCE_SITES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company
              </label>
              <input
                type="text"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Role Filter
              </label>
              <input
                type="text"
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Check Interval (hours)
            </label>
            <input
              type="number"
              min={1}
              value={intervalHours}
              onChange={(e) => setIntervalHours(Number(e.target.value) || 24)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => {
                reset();
                onClose();
              }}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || !url.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm"
            >
              {submitting ? "Adding..." : "Add"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

/* ================================================================
   Scraper Manager Panel
   ================================================================ */

function ScraperPanel() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [showAddModal, setShowAddModal] = useState(false);

  // Seeds list
  const {
    data: seeds,
    isLoading: seedsLoading,
  } = useQuery({
    queryKey: ["scraper-seeds"],
    queryFn: () => api.get<SeedURL[]>("/scraper/seeds"),
  });

  // Job status
  const { data: jobs } = useQuery({
    queryKey: ["scraper-status"],
    queryFn: () => api.get<ScraperJob[]>("/scraper/status"),
    refetchInterval: 5000,
  });

  // Delete seed
  const deleteSeed = useMutation({
    mutationFn: (id: number) => api.del(`/scraper/seeds/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scraper-seeds"] });
      toast.success("Seed URL deleted");
    },
    onError: (err: Error) => {
      toast.error(
        err instanceof ApiRequestError ? err.message : "Delete failed",
      );
    },
  });

  // Run scraper
  const runScraper = useMutation({
    mutationFn: (seedUrlIds: number[] | null) =>
      api.post("/scraper/run", { seed_url_ids: seedUrlIds }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scraper-status"] });
      toast.success("Scraper job started");
    },
    onError: (err: Error) => {
      toast.error(
        err instanceof ApiRequestError ? err.message : "Failed to start scraper",
      );
    },
  });

  const hasRunning = jobs?.some((j) => j.status === "running");

  return (
    <section className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-800">
            Scraper Management
          </h2>
          <p className="text-sm text-gray-500">
            Manage seed URLs and run the scraper to collect interview questions.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowAddModal(true)}
            className="px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
          >
            + Add Seed
          </button>
          <button
            onClick={() => runScraper.mutate(null)}
            disabled={runScraper.isPending || hasRunning}
            className="px-3 py-1.5 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 text-sm"
          >
            {hasRunning ? "Running..." : "Run Scraper"}
          </button>
        </div>
      </div>

      {/* Seed URL table */}
      {seedsLoading ? (
        <LoadingSpinner />
      ) : !seeds || seeds.length === 0 ? (
        <p className="text-sm text-gray-400 py-4 text-center">
          No seed URLs configured yet.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left text-gray-500">
                <th className="pb-2 font-medium">URL</th>
                <th className="pb-2 font-medium">Source</th>
                <th className="pb-2 font-medium">Company</th>
                <th className="pb-2 font-medium">Interval</th>
                <th className="pb-2 font-medium">Last Checked</th>
                <th className="pb-2 font-medium w-16"></th>
              </tr>
            </thead>
            <tbody>
              {seeds.map((seed) => (
                <tr
                  key={seed.id}
                  className="border-b border-gray-100 hover:bg-gray-50"
                >
                  <td className="py-2 pr-2 max-w-xs truncate text-gray-700">
                    <a
                      href={seed.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-blue-600 hover:underline"
                    >
                      {seed.url}
                    </a>
                  </td>
                  <td className="py-2 pr-2 text-gray-600">{seed.source_site}</td>
                  <td className="py-2 pr-2 text-gray-600">
                    {seed.company ?? "-"}
                  </td>
                  <td className="py-2 pr-2 text-gray-600">
                    {seed.check_interval_hours}h
                  </td>
                  <td className="py-2 pr-2 text-gray-500">
                    {seed.last_checked_at
                      ? new Date(seed.last_checked_at).toLocaleDateString()
                      : "Never"}
                  </td>
                  <td className="py-2">
                    <button
                      onClick={() => deleteSeed.mutate(seed.id)}
                      className="text-red-500 hover:text-red-700 text-xs"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Job status */}
      {jobs && jobs.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">
            Recent Jobs
          </h3>
          <div className="space-y-2">
            {jobs.map((job) => (
              <div
                key={job.job_id}
                className={`p-3 rounded text-sm border ${
                  job.status === "running"
                    ? "bg-blue-50 border-blue-200"
                    : job.status === "completed"
                      ? "bg-green-50 border-green-200"
                      : "bg-red-50 border-red-200"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">
                    {job.status === "running"
                      ? `Running (${job.seeds_processed}/${job.seeds_total} seeds)`
                      : job.status === "completed"
                        ? "Completed"
                        : "Failed"}
                  </span>
                  <span className="text-gray-500 text-xs">
                    {new Date(job.started_at).toLocaleString()}
                  </span>
                </div>
                <p className="text-gray-600 mt-1">
                  {job.questions_found} questions found
                </p>
                {job.errors.length > 0 && (
                  <div className="mt-1 text-red-600 text-xs">
                    {job.errors.map((err, i) => (
                      <p key={i}>{err}</p>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <AddSeedModal
        open={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSuccess={() =>
          queryClient.invalidateQueries({ queryKey: ["scraper-seeds"] })
        }
      />
    </section>
  );
}

/* ================================================================
   Settings Page
   ================================================================ */

export default function Settings() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Settings</h1>
      <ExportPanel />
      <ImportPanel />
      <SeedDataPanel />
      <ScraperPanel />
    </div>
  );
}
