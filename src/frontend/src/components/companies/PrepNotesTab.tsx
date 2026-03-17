import { useState, useRef, type RefObject } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { usePrepNotes } from "../../hooks/usePrepNotes";
import { useScrollRestore } from "../../hooks/useScrollRestore";
import MarkdownPreview from "../ui/MarkdownPreview";
import type { Company } from "../../types/company";

type ImportMode = "append" | "replace";

interface PrepNotesTabProps {
  companyId: number;
  initialNotes: string | null;
  onNotesChanged?: (notes: string) => void;
  scrollContainerRef?: RefObject<HTMLElement | null>;
}

/**
 * PrepNotesTab: edit/preview markdown prep notes with autosave.
 * Inline panel variant used in the Companies page.
 */
export default function PrepNotesTab({
  companyId,
  initialNotes,
  onNotesChanged,
  scrollContainerRef,
}: PrepNotesTabProps) {
  const queryClient = useQueryClient();
  const [importMode, setImportMode] = useState<ImportMode>("append");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const captureScrollRef = useRef<(() => void) | null>(null);

  const fallbackRef = useRef<HTMLElement>(null);
  const effectiveContainerRef = scrollContainerRef ?? fallbackRef;

  const {
    notes,
    setNotes,
    mode,
    switchMode,
    saveStatus,
    setSaveStatus,
    handleRetry,
  } = usePrepNotes({ companyId, initialNotes, onNotesChanged, captureScrollRef });

  const { captureScroll } = useScrollRestore(effectiveContainerRef, textareaRef, mode);
  captureScrollRef.current = captureScroll;

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
      onNotesChanged?.(newNotes);
    } catch {
      setSaveStatus("error");
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  return (
    <div className="space-y-3">
      {/* Toolbar -- sticky within the parent scroll container */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 pb-2 flex items-center justify-between">
        <div className="flex gap-1">
          <button
            onClick={() => switchMode("preview")}
            className={`text-xs px-2 py-1 rounded ${
              mode === "preview"
                ? "bg-blue-100 text-blue-700 font-medium"
                : "text-gray-500 hover:bg-gray-100"
            }`}
          >
            Preview
          </button>
          <button
            onClick={() => switchMode("edit")}
            className={`text-xs px-2 py-1 rounded ${
              mode === "edit"
                ? "bg-blue-100 text-blue-700 font-medium"
                : "text-gray-500 hover:bg-gray-100"
            }`}
          >
            Edit
          </button>
          <Link
            to={`/companies/${companyId}/prep`}
            className="text-xs px-2 py-1 rounded text-gray-500 hover:bg-gray-100"
          >
            Full Page
          </Link>
        </div>

        {/* Save status */}
        <span className="text-xs">
          {saveStatus === "saving" && (
            <span className="text-gray-400">Saving...</span>
          )}
          {saveStatus === "saved" && (
            <span className="text-green-600">Saved</span>
          )}
          {saveStatus === "error" && (
            <span className="text-red-600">
              Save failed{" "}
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

      {/* Content area */}
      {mode === "edit" ? (
        <textarea
          ref={textareaRef}
          value={notes}
          onChange={(e) => {
            setNotes(e.target.value);
            if (saveStatus === "saved" || saveStatus === "error") {
              setSaveStatus("idle");
            }
          }}
          rows={12}
          className="w-full border border-gray-300 rounded px-3 py-2 text-sm font-mono resize-y"
          placeholder="Write markdown prep notes here...&#10;&#10;- [ ] Review system design&#10;- [ ] Practice coding questions"
        />
      ) : (
        <div className="text-sm min-h-[8rem] border border-gray-200 rounded p-3 overflow-y-auto">
          {notes ? (
            <MarkdownPreview markdown={notes} />
          ) : (
            <p className="text-gray-400 italic">
              No prep notes yet. Switch to Edit mode to add some.
            </p>
          )}
        </div>
      )}

      {/* Import section */}
      <div className="border-t border-gray-200 pt-3 space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-gray-600">Import .md:</span>
          <label className="flex items-center gap-1 text-xs text-gray-500">
            <input
              type="radio"
              name={`import-mode-${companyId}`}
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
              name={`import-mode-${companyId}`}
              value="replace"
              checked={importMode === "replace"}
              onChange={() => setImportMode("replace")}
              className="w-3 h-3"
            />
            Replace
          </label>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".md,.markdown,.txt"
          onChange={handleImport}
          className="text-xs text-gray-500 file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:text-xs file:bg-blue-50 file:text-blue-700 file:cursor-pointer"
        />
      </div>
    </div>
  );
}
