import { useState, useEffect, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../utils/api";
import { useDebounce } from "./useDebounce";
import type { FrameworkNode } from "../types/framework";

type ViewMode = "preview" | "edit";
type SaveStatus = "idle" | "saving" | "saved" | "error";

interface UseFrameworkNotesOptions {
  nodeId: number;
  initialNotes: string | null;
}

/**
 * Hook for framework node notes: debounced auto-save, checkbox persistence.
 *
 * Mirrors usePrepNotes but saves to PUT /framework/nodes/{id} with description.
 */
export function useFrameworkNotes({
  nodeId,
  initialNotes,
}: UseFrameworkNotesOptions) {
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<ViewMode>("preview");
  const [notes, setNotes] = useState(initialNotes ?? "");
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");

  const lastSavedRef = useRef(initialNotes ?? "");
  const isSavingRef = useRef(false);

  // Sync from parent (initial load or external refetch).
  useEffect(() => {
    if (isSavingRef.current) return;
    const incoming = initialNotes ?? "";
    if (incoming !== lastSavedRef.current) {
      setNotes(incoming);
      lastSavedRef.current = incoming;
    }
  }, [initialNotes]);

  // Debounced auto-save
  const debouncedNotes = useDebounce(notes, 500);

  const saveMutation = useMutation({
    mutationFn: (description: string) =>
      api.put<FrameworkNode>(`/framework/nodes/${nodeId}`, { description }),
    onMutate: async (description) => {
      isSavingRef.current = true;
      // Cancel any outbound refetches so they don't overwrite optimistic update
      await queryClient.cancelQueries({
        queryKey: ["framework", "node", nodeId],
      });
    },
    onSuccess: (_data, description) => {
      lastSavedRef.current = description;
      // Update the single-node query cache
      queryClient.setQueryData<FrameworkNode>(
        ["framework", "node", nodeId],
        (old) => (old ? { ...old, description } : old),
      );
      setSaveStatus("saved");
      isSavingRef.current = false;
    },
    onError: () => {
      setSaveStatus("error");
      isSavingRef.current = false;
    },
  });

  // Auto-save when debounced notes change (and differ from last saved)
  useEffect(() => {
    if (debouncedNotes !== lastSavedRef.current) {
      setSaveStatus("saving");
      saveMutation.mutate(debouncedNotes);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedNotes, nodeId]);

  /** Toggle a checkbox line in the markdown. */
  function handleCheckboxClick(lineIndex: number) {
    const lines = notes.split("\n");
    if (lineIndex < 0 || lineIndex >= lines.length) return;
    const line = lines[lineIndex];
    if (/\[x\]/i.test(line)) {
      lines[lineIndex] = line.replace(/\[[xX]\]/, "[ ]");
    } else if (/\[ \]/.test(line)) {
      lines[lineIndex] = line.replace("[ ]", "[x]");
    }
    const updated = lines.join("\n");
    setNotes(updated);
    // Immediately save checkbox changes
    setSaveStatus("saving");
    saveMutation.mutate(updated);
  }

  /** Retry a failed save. */
  function handleRetry() {
    setSaveStatus("saving");
    saveMutation.mutate(notes);
  }

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
