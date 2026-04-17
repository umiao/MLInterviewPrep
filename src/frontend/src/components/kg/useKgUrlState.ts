// URL <-> graph state sync. Keeps ?node={id}&expanded={ids} in sync with
// selection and expansion so views are shareable and restorable on reload.

import { useCallback, useEffect, useRef } from "react";

export interface UrlState {
  nodeId: string | null;
  expanded: Set<string> | null;
}

export function readUrlState(search: string): UrlState {
  const params = new URLSearchParams(search);
  const rawNode = params.get("node");
  const nodeId = rawNode && /^n\d+$/.test(rawNode) ? rawNode : null;
  const rawExpanded = params.get("expanded");
  let expanded: Set<string> | null = null;
  if (rawExpanded != null) {
    expanded = new Set(
      rawExpanded
        .split(",")
        .map((s) => s.trim())
        .filter((s) => /^n\d+$/.test(s)),
    );
  }
  return { nodeId, expanded };
}

export function writeUrlState(state: UrlState): string {
  const params = new URLSearchParams();
  if (state.nodeId) params.set("node", state.nodeId);
  if (state.expanded) {
    params.set("expanded", [...state.expanded].sort().join(","));
  }
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export function useSyncUrl(state: UrlState) {
  const lastRef = useRef<string>("");
  useEffect(() => {
    const qs = writeUrlState(state);
    const next = `${window.location.pathname}${qs}`;
    if (next === lastRef.current) return;
    lastRef.current = next;
    window.history.replaceState(null, "", next);
  }, [state]);
}

export function useInitialUrlState(): UrlState {
  const ref = useRef<UrlState | null>(null);
  if (ref.current === null) {
    ref.current = readUrlState(typeof window === "undefined" ? "" : window.location.search);
  }
  return ref.current;
}

export function useUrlStateNotifier() {
  // Hook kept for future listening if needed. No-op for now.
  return useCallback(() => undefined, []);
}
