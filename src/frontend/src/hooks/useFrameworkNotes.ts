import { useState, useEffect, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../utils/api";
import { useDebounce } from "./useDebounce";
import { countChecked, countUnchecked } from "../utils/markdown";
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
  const saveVersionRef = useRef(0);
  const nodeIdRef = useRef(nodeId);

  // Sync from parent (initial load, external refetch, or nodeId change).
  useEffect(() => {
    if (nodeIdRef.current !== nodeId) {
      // Node changed — reset state, bump version to invalidate pending saves
      nodeIdRef.current = nodeId;
      saveVersionRef.current += 1;
      const incoming = initialNotes ?? "";
      setNotes(incoming);
      lastSavedRef.current = incoming;
      setSaveStatus("idle");
      setMode("preview");
      isSavingRef.current = false;
      return;
    }
    // Same node, external refresh
    if (isSavingRef.current) return;
    const incoming = initialNotes ?? "";
    if (incoming !== lastSavedRef.current) {
      setNotes(incoming);
      lastSavedRef.current = incoming;
    }
  }, [nodeId, initialNotes]);

  // Debounced auto-save
  const debouncedNotes = useDebounce(notes, 500);

  interface SavePayload {
    description: string;
    progress_pct?: number;
  }

  const saveMutation = useMutation({
    mutationFn: (payload: SavePayload) =>
      api.put<FrameworkNode>(`/framework/nodes/${nodeId}`, payload),
    onMutate: async () => {
      isSavingRef.current = true;
      // Cancel any outbound refetches so they don't overwrite optimistic update
      await queryClient.cancelQueries({
        queryKey: ["framework", "node", nodeId],
      });
    },
    onSuccess: (_data, payload) => {
      lastSavedRef.current = payload.description;
      // Update the single-node query cache
      queryClient.setQueryData<FrameworkNode>(
        ["framework", "node", nodeId],
        (old) => (old ? { ...old, description: payload.description } : old),
      );
      // Invalidate tree so parent progress bars refresh
      if (payload.progress_pct !== undefined) {
        queryClient.invalidateQueries({ queryKey: ["framework", "tree"] });
      }
      setSaveStatus("saved");
      isSavingRef.current = false;
    },
    onError: () => {
      setSaveStatus("error");
      isSavingRef.current = false;
    },
  });

  // Auto-save when debounced notes change (and differ from last saved).
  // Version guard: if nodeId changed since debounce started, skip the save.
  useEffect(() => {
    const version = saveVersionRef.current;
    if (debouncedNotes !== lastSavedRef.current) {
      if (version !== saveVersionRef.current) return;
      setSaveStatus("saving");
      saveMutation.mutate({ description: debouncedNotes });
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
    // Calculate progress from checkbox state
    const checked = countChecked(updated);
    const unchecked = countUnchecked(updated);
    const total = checked + unchecked;
    const progress_pct = total > 0 ? Math.round((checked / total) * 100 * 10) / 10 : undefined;
    // Immediately save checkbox changes with progress
    setSaveStatus("saving");
    saveMutation.mutate({ description: updated, progress_pct });
  }

  /** Retry a failed save. */
  function handleRetry() {
    setSaveStatus("saving");
    saveMutation.mutate({ description: notes });
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
