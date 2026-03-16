import { useState, useEffect, useRef, useCallback } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../utils/api";
import { useDebounce } from "./useDebounce";
import { toggleCheckbox } from "../utils/markdown";
import type { Company } from "../types/company";

type ViewMode = "preview" | "edit";
type SaveStatus = "idle" | "saving" | "saved" | "error";

interface UsePrepNotesOptions {
  companyId: number;
  initialNotes: string | null;
  onNotesChanged?: (notes: string) => void;
}

/**
 * Shared hook for prep notes: fetch/save/autosave/checkbox-toggle logic.
 */
export function usePrepNotes({
  companyId,
  initialNotes,
  onNotesChanged,
}: UsePrepNotesOptions) {
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<ViewMode>("preview");
  const [notes, setNotes] = useState(initialNotes ?? "");
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");

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

  /** Retry a failed save. */
  function handleRetry() {
    setSaveStatus("saving");
    saveMutation.mutate(notes);
  }

  /** Toggle checkbox in preview mode (immediate save, bypasses debounce). */
  const handleCheckboxClick = useCallback(
    (lineIndex: number) => {
      const updated = toggleCheckbox(notes, lineIndex);
      setNotes(updated);
      setSaveStatus("saving");
      saveMutation.mutate(updated);
      lastSavedRef.current = updated;
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [notes, companyId],
  );

  return {
    notes,
    setNotes,
    mode,
    setMode,
    saveStatus,
    setSaveStatus,
    handleRetry,
    handleCheckboxClick,
  };
}
