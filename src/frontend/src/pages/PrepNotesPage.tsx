import { useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../utils/api";
import { usePrepNotes } from "../hooks/usePrepNotes";
import MarkdownPreview from "../components/ui/MarkdownPreview";
import type { Company } from "../types/company";

type ImportMode = "append" | "replace";

/**
 * Full-screen prep notes page at /companies/:companyId/prep.
 */
export default function PrepNotesPage() {
  const { companyId: rawId } = useParams<{ companyId: string }>();
  const companyId = Number(rawId);
  const queryClient = useQueryClient();
  const [importMode, setImportMode] = useState<ImportMode>("append");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data: company, isLoading } = useQuery<Company>({
    queryKey: ["companies", companyId],
    queryFn: () => api.get<Company>(`/companies/${companyId}`),
    enabled: companyId > 0,
  });

  const {
    notes,
    setNotes,
    mode,
    setMode,
    saveStatus,
    setSaveStatus,
    handleRetry,
    handleCheckboxClick,
  } = usePrepNotes({
    companyId,
    initialNotes: company?.prep_notes ?? null,
  });

  /** Import .md file handler. */
  async function handleImport(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("mode", importMode);
      const res = await fetch(
        `/api/companies/${companyId}/prep-notes/import`,
        { method: "POST", body: formData },
      );
      if (!res.ok) {
        const detail = await res.json().catch(() => null);
        throw new Error(
          (detail as Record<string, string>)?.detail ?? res.statusText,
        );
      }
      const updated: Company = await res.json();
      const newNotes = updated.prep_notes ?? "";
      setNotes(newNotes);
      setSaveStatus("saved");
      queryClient.invalidateQueries({ queryKey: ["companies"] });
    } catch {
      setSaveStatus("error");
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        Loading...
      </div>
    );
  }

  if (!company) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <p className="text-gray-500">Company not found.</p>
        <Link to="/companies" className="text-blue-600 hover:text-blue-800 text-sm">
          Back to Companies
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-3rem)]">
      {/* Sticky header */}
      <header className="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shrink-0">
        <Link
          to="/companies"
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          &larr; Companies
        </Link>

        <h1 className="text-lg font-semibold text-gray-800">
          {company.name} - Prep Notes
        </h1>

        <div className="flex items-center gap-3">
          {/* Mode toggle */}
          <div className="flex gap-1">
            <button
              onClick={() => setMode("preview")}
              className={`text-sm px-3 py-1.5 rounded ${
                mode === "preview"
                  ? "bg-blue-100 text-blue-700 font-medium"
                  : "text-gray-500 hover:bg-gray-100"
              }`}
            >
              Preview
            </button>
            <button
              onClick={() => setMode("edit")}
              className={`text-sm px-3 py-1.5 rounded ${
                mode === "edit"
                  ? "bg-blue-100 text-blue-700 font-medium"
                  : "text-gray-500 hover:bg-gray-100"
              }`}
            >
              Edit
            </button>
          </div>

          {/* Save status */}
          <span className="text-sm min-w-[5rem] text-right">
            {saveStatus === "saving" && (
              <span className="text-gray-400">Saving...</span>
            )}
            {saveStatus === "saved" && (
              <span className="text-green-600">Saved</span>
            )}
            {saveStatus === "error" && (
              <span className="text-red-600">
                Failed{" "}
                <button
                  onClick={handleRetry}
                  className="underline hover:text-red-800"
                >
                  retry
                </button>
              </span>
            )}
          </span>
        </div>
      </header>

      {/* Content area */}
      <div className="flex-1 overflow-auto p-6 flex flex-col min-h-0">
        {mode === "edit" ? (
          <textarea
            value={notes}
            onChange={(e) => {
              setNotes(e.target.value);
              if (saveStatus === "saved" || saveStatus === "error") {
                setSaveStatus("idle");
              }
            }}
            className="flex-1 min-h-0 w-full border border-gray-300 rounded px-4 py-3 text-base font-mono resize-none"
            placeholder="Write markdown prep notes here...&#10;&#10;- [ ] Review system design&#10;- [ ] Practice coding questions"
          />
        ) : (
          <div className="prep-prose min-h-0 overflow-auto">
            {notes ? (
              <MarkdownPreview
                markdown={notes}
                onCheckboxClick={handleCheckboxClick}
              />
            ) : (
              <p className="text-gray-400 italic">
                No prep notes yet. Switch to Edit mode to add some.
              </p>
            )}
          </div>
        )}
      </div>

      {/* Import section */}
      <div className="border-t border-gray-200 px-6 py-3 bg-white shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-xs font-medium text-gray-600">Import .md:</span>
          <label className="flex items-center gap-1 text-xs text-gray-500">
            <input
              type="radio"
              name="import-mode-page"
              value="append"
              checked={importMode === "append"}
              onChange={() => setImportMode("append")}
              className="w-3 h-3"
            />
            Append
          </label>
          <label className="flex items-center gap-1 text-xs text-gray-500">
            <input
              type="radio"
              name="import-mode-page"
              value="replace"
              checked={importMode === "replace"}
              onChange={() => setImportMode("replace")}
              className="w-3 h-3"
            />
            Replace
          </label>
          <input
            ref={fileInputRef}
            type="file"
            accept=".md,.markdown,.txt"
            onChange={handleImport}
            className="text-xs text-gray-500 file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:text-xs file:bg-blue-50 file:text-blue-700 file:cursor-pointer"
          />
        </div>
      </div>
    </div>
  );
}
