import { useState, useEffect, useRef, useCallback } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import { api } from "../../utils/api";
import { useDebounce } from "../../hooks/useDebounce";
import { toggleCheckbox } from "../../utils/markdown";
import type { Company } from "../../types/company";

type ViewMode = "preview" | "edit";
type SaveStatus = "idle" | "saving" | "saved" | "error";
type ImportMode = "append" | "replace";

interface PrepNotesTabProps {
  companyId: number;
  initialNotes: string | null;
  onNotesChanged?: (notes: string) => void;
}

/**
 * PrepNotesTab: edit/preview markdown prep notes with checkbox click-toggle.
 */
export default function PrepNotesTab({
  companyId,
  initialNotes,
  onNotesChanged,
}: PrepNotesTabProps) {
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<ViewMode>("preview");
  const [notes, setNotes] = useState(initialNotes ?? "");
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");
  const [importMode, setImportMode] = useState<ImportMode>("append");
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Track the last saved value to avoid re-saving on prop change
  const lastSavedRef = useRef(initialNotes ?? "");

  // Sync from parent when initialNotes changes (e.g., after refetch)
  useEffect(() => {
    const incoming = initialNotes ?? "";
    if (incoming !== lastSavedRef.current) {
      setNotes(incoming);
      lastSavedRef.current = incoming;
    }
  }, [initialNotes]);

  // Debounced auto-save
  const debouncedNotes = useDebounce(notes, 500);

  const saveMutation = useMutation({
    mutationFn: (prepNotes: string) =>
      api.put<Company>(`/companies/${companyId}`, { prep_notes: prepNotes }),
    onSuccess: (_data, prepNotes) => {
      lastSavedRef.current = prepNotes;
      setSaveStatus("saved");
      queryClient.invalidateQueries({ queryKey: ["companies"] });
      onNotesChanged?.(prepNotes);
    },
    onError: () => {
      setSaveStatus("error");
    },
  });

  // Auto-save when debounced notes change (and differ from last saved)
  useEffect(() => {
    if (debouncedNotes !== lastSavedRef.current) {
      setSaveStatus("saving");
      saveMutation.mutate(debouncedNotes);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedNotes, companyId]);

  function handleRetry() {
    setSaveStatus("saving");
    saveMutation.mutate(notes);
  }

  // Checkbox toggle in preview mode
  const handleCheckboxClick = useCallback(
    (lineIndex: number) => {
      const updated = toggleCheckbox(notes, lineIndex);
      setNotes(updated);
      // Save immediately on toggle (bypass debounce)
      setSaveStatus("saving");
      saveMutation.mutate(updated);
      lastSavedRef.current = updated;
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [notes, companyId],
  );

  // Import handler
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
      lastSavedRef.current = newNotes;
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
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <div className="flex gap-1">
          <button
            onClick={() => setMode("preview")}
            className={`text-xs px-2 py-1 rounded ${
              mode === "preview"
                ? "bg-blue-100 text-blue-700 font-medium"
                : "text-gray-500 hover:bg-gray-100"
            }`}
          >
            Preview
          </button>
          <button
            onClick={() => setMode("edit")}
            className={`text-xs px-2 py-1 rounded ${
              mode === "edit"
                ? "bg-blue-100 text-blue-700 font-medium"
                : "text-gray-500 hover:bg-gray-100"
            }`}
          >
            Edit
          </button>
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
        <div className="prose prose-sm max-w-none text-sm min-h-[8rem] border border-gray-200 rounded p-3 overflow-y-auto">
          {notes ? (
            <MarkdownPreview markdown={notes} onCheckboxClick={handleCheckboxClick} />
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

/* ---------- Markdown Preview with clickable checkboxes ---------- */

function MarkdownPreview({
  markdown,
  onCheckboxClick,
}: {
  markdown: string;
  onCheckboxClick: (lineIndex: number) => void;
}) {
  // Build a map: which list items correspond to checkbox lines
  const lines = markdown.split("\n");
  const checkboxLineIndices: number[] = [];
  for (let i = 0; i < lines.length; i++) {
    const trimmed = lines[i].trimStart();
    if (/^[-*]\s*\[[ xX]\]/.test(trimmed)) {
      checkboxLineIndices.push(i);
    }
  }

  // Track which checkbox item we're rendering
  let checkboxCounter = 0;

  return (
    <ReactMarkdown
      components={{
        li: ({ children, ...props }) => {
          // Detect if this li contains a checkbox (input type=checkbox)
          const childArray = Array.isArray(children) ? children : [children];
          const hasCheckbox = childArray.some(
            (child) =>
              typeof child === "object" &&
              child !== null &&
              "type" in child &&
              (child as React.ReactElement).type === "input",
          );

          if (hasCheckbox && checkboxCounter < checkboxLineIndices.length) {
            const lineIdx = checkboxLineIndices[checkboxCounter];
            checkboxCounter++;
            const isChecked = /^[-*]\s*\[[xX]\]/.test(
              lines[lineIdx].trimStart(),
            );

            return (
              <li
                {...props}
                className="list-none flex items-start gap-1.5 cursor-pointer select-none"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onCheckboxClick(lineIdx);
                }}
              >
                <span className="mt-0.5 shrink-0">
                  {isChecked ? (
                    <span className="inline-block w-4 h-4 border-2 border-blue-500 bg-blue-500 rounded text-white text-xs leading-4 text-center">
                      x
                    </span>
                  ) : (
                    <span className="inline-block w-4 h-4 border-2 border-gray-300 rounded" />
                  )}
                </span>
                <span className={isChecked ? "line-through text-gray-400" : ""}>
                  {childArray.filter(
                    (child) =>
                      !(
                        typeof child === "object" &&
                        child !== null &&
                        "type" in child &&
                        (child as React.ReactElement).type === "input"
                      ),
                  )}
                </span>
              </li>
            );
          }

          return <li {...props}>{children}</li>;
        },
      }}
    >
      {markdown}
    </ReactMarkdown>
  );
}
