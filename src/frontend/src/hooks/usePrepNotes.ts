import { useState, useEffect, useRef, type MutableRefObject } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../utils/api";
import { useDebounce } from "./useDebounce";
import type { Company } from "../types/company";

export type ViewMode = "preview" | "edit";
type SaveStatus = "idle" | "saving" | "saved" | "error";

interface UsePrepNotesOptions {
  companyId: number;
  initialNotes: string | null;
  onNotesChanged?: (notes: string) => void;
  /**
   * Optional ref to a capture function (from useScrollRestore). When provided,
   * switchMode() calls it automatically before changing mode. This guarantees
   * scroll capture without callers needing to remember to pass it.
   */
  captureScrollRef?: MutableRefObject<(() => void) | null>;
}

/**
 * Shared hook for prep notes: fetch/save/autosave logic.
 *
 * Saves update the query cache directly from the server response instead of
 * calling invalidateQueries.  This avoids a refetch race where stale GET
 * data could overwrite local state before the UI re-renders.
 */
export function usePrepNotes({
  companyId,
  initialNotes,
  onNotesChanged,
  captureScrollRef,
}: UsePrepNotesOptions) {
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<ViewMode>("preview");
  const [notes, setNotes] = useState(initialNotes ?? "");
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");

  const lastSavedRef = useRef(initialNotes ?? "");

  // Sync from parent (e.g. initial load, import, or external refetch).
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
    onSuccess: (data, prepNotes) => {
      lastSavedRef.current = prepNotes;
      // Merge the confirmed server state into the query cache (PUT response
      // may lack fields like topic_weights that GET returns, so we merge
      // instead of replacing to avoid clobbering cached data).
      queryClient.setQueryData<Company>(["companies", companyId], (old) =>
        old ? { ...old, ...data } : data,
      );
      setSaveStatus("saved");
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

  /** Retry a failed save. */
  function handleRetry() {
    setSaveStatus("saving");
    saveMutation.mutate(notes);
  }

  /**
   * Switch between preview/edit modes. Automatically captures scroll position
   * (via captureScrollRef) before changing mode.
   */
  function switchMode(newMode: ViewMode) {
    if (newMode === mode) return;
    captureScrollRef?.current?.();
    setMode(newMode);
  }

  return {
    notes,
    setNotes,
    mode,
    switchMode,
    saveStatus,
    setSaveStatus,
    handleRetry,
  };
}
