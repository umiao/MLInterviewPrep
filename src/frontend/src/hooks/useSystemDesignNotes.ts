import { useState, useEffect, useRef, useCallback } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../utils/api";
import { useDebounce } from "./useDebounce";
import type { SystemDesign, SystemDesignSection } from "../types/system-design";

export type ViewMode = "preview" | "edit";
type SaveStatus = "idle" | "saving" | "saved" | "error";

/** Per-section save status for UI feedback. */
export type SectionSaveStatuses = Record<SystemDesignSection, SaveStatus>;

interface UseSystemDesignNotesOptions {
  slug: string;
  initialData: SystemDesign | null;
}

const ALL_SECTIONS: SystemDesignSection[] = [
  "overview",
  "architecture",
  "dataflow",
  "formulas",
  "production_constraints",
  "tradeoffs",
  "defense",
  "verbal_outline",
  "cheat_sheet",
];

function buildSectionContents(
  data: SystemDesign | null,
): Record<SystemDesignSection, string> {
  const out = {} as Record<SystemDesignSection, string>;
  for (const s of ALL_SECTIONS) {
    out[s] = data?.[s] ?? "";
  }
  return out;
}

function buildSaveStatuses(): SectionSaveStatuses {
  const out = {} as SectionSaveStatuses;
  for (const s of ALL_SECTIONS) {
    out[s] = "idle";
  }
  return out;
}

/**
 * Hook for system design section editing with debounced auto-save.
 *
 * Manages all section contents, edit/preview mode, per-section save status,
 * and the currently highlighted section (for bookmark nav).
 */
export function useSystemDesignNotes({
  slug,
  initialData,
}: UseSystemDesignNotesOptions) {
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<ViewMode>("preview");
  const [highlightedSection, setHighlightedSection] =
    useState<SystemDesignSection>("overview");
  const [sectionContents, setSectionContents] = useState(() =>
    buildSectionContents(initialData),
  );
  const [saveStatuses, setSaveStatuses] = useState<SectionSaveStatuses>(
    buildSaveStatuses,
  );

  // Track last-saved content per section to avoid unnecessary saves
  const lastSavedRef = useRef<Record<SystemDesignSection, string>>(
    buildSectionContents(initialData),
  );

  // Sync when initialData loads (e.g., from server fetch)
  useEffect(() => {
    const contents = buildSectionContents(initialData);
    setSectionContents(contents);
    lastSavedRef.current = { ...contents };
  }, [initialData]);

  // --- Per-section debounced auto-save ---
  // We debounce the entire sectionContents object, then diff against lastSaved.
  const debouncedContents = useDebounce(sectionContents, 500);

  const saveMutation = useMutation({
    mutationFn: (payload: { section: SystemDesignSection; content: string }) =>
      api.put<SystemDesign>(`/system-designs/${slug}`, {
        [payload.section]: payload.content,
      }),
    onSuccess: (data, payload) => {
      lastSavedRef.current[payload.section] = payload.content;
      queryClient.setQueryData<SystemDesign>(
        ["system-design", slug],
        (old) => (old ? { ...old, ...data } : data),
      );
      setSaveStatuses((prev) => ({ ...prev, [payload.section]: "saved" }));
    },
    onError: (_err, payload) => {
      setSaveStatuses((prev) => ({ ...prev, [payload.section]: "error" }));
    },
  });

  // Auto-save any sections that changed
  useEffect(() => {
    for (const section of ALL_SECTIONS) {
      if (debouncedContents[section] !== lastSavedRef.current[section]) {
        setSaveStatuses((prev) => ({ ...prev, [section]: "saving" }));
        saveMutation.mutate({ section, content: debouncedContents[section] });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedContents, slug]);

  /** Update content for a specific section. */
  const updateSection = useCallback(
    (section: SystemDesignSection, content: string) => {
      setSectionContents((prev) => ({ ...prev, [section]: content }));
      setSaveStatuses((prev) => {
        const cur = prev[section];
        if (cur === "saved" || cur === "error") {
          return { ...prev, [section]: "idle" };
        }
        return prev;
      });
    },
    [],
  );

  /** Switch between preview/edit modes. Flush unsaved on mode switch. */
  const switchMode = useCallback(
    (newMode: ViewMode) => {
      if (newMode === mode) return;
      // Flush any dirty sections immediately when leaving edit mode
      if (mode === "edit") {
        for (const section of ALL_SECTIONS) {
          if (sectionContents[section] !== lastSavedRef.current[section]) {
            setSaveStatuses((prev) => ({ ...prev, [section]: "saving" }));
            saveMutation.mutate({
              section,
              content: sectionContents[section],
            });
          }
        }
      }
      setMode(newMode);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [mode, sectionContents],
  );

  /** Retry a failed save for a specific section. */
  const retrySection = useCallback(
    (section: SystemDesignSection) => {
      setSaveStatuses((prev) => ({ ...prev, [section]: "saving" }));
      saveMutation.mutate({ section, content: sectionContents[section] });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [sectionContents],
  );

  /** Aggregate save status for the header indicator. */
  const aggregateSaveStatus: SaveStatus = ALL_SECTIONS.some(
    (s) => saveStatuses[s] === "error",
  )
    ? "error"
    : ALL_SECTIONS.some((s) => saveStatuses[s] === "saving")
      ? "saving"
      : ALL_SECTIONS.some((s) => saveStatuses[s] === "saved")
        ? "saved"
        : "idle";

  return {
    mode,
    switchMode,
    highlightedSection,
    setHighlightedSection,
    sectionContents,
    updateSection,
    saveStatuses,
    aggregateSaveStatus,
    retrySection,
  };
}
