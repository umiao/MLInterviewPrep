export type PrepTab =
  | "notes"
  | "knowledge"
  | "forum"
  | "docs"
  | "coding"
  | "index";

export interface PrepParams {
  tab: PrepTab;
  docId: number | null;
  problemId: number | null;
}

const VALID_TABS: readonly PrepTab[] = [
  "notes",
  "knowledge",
  "forum",
  "docs",
  "coding",
  "index",
];

function parsePositiveInt(raw: string | null): number | null {
  if (!raw || !/^\d+$/.test(raw)) return null;
  const n = Number(raw);
  return n > 0 ? n : null;
}

/**
 * Parse the prep-page URL search string into a canonical shape.
 *
 * Back-compat: `?doc=N` (no `tab`) is treated as `?tab=docs&doc=N`.
 * `?problem=N` is only honored when `tab=coding`.
 */
export function parsePrepParams(search: string): PrepParams {
  const sp = new URLSearchParams(search);
  const rawTab = sp.get("tab");
  const docId = parsePositiveInt(sp.get("doc"));
  const problemIdRaw = parsePositiveInt(sp.get("problem"));

  let tab: PrepTab;
  if (rawTab && (VALID_TABS as readonly string[]).includes(rawTab)) {
    tab = rawTab as PrepTab;
  } else if (docId !== null) {
    tab = "docs";
  } else {
    tab = "notes";
  }

  return {
    tab,
    docId: tab === "docs" ? docId : null,
    problemId: tab === "coding" ? problemIdRaw : null,
  };
}

/** Build a URLSearchParams for the given prep state (omits empty values). */
export function serializePrepParams(p: PrepParams): URLSearchParams {
  const out = new URLSearchParams();
  out.set("tab", p.tab);
  if (p.tab === "docs" && p.docId !== null) out.set("doc", String(p.docId));
  if (p.tab === "coding" && p.problemId !== null)
    out.set("problem", String(p.problemId));
  return out;
}
