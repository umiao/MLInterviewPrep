// Palette + layout config for the knowledge graph.
// Full palette polish (Tailwind-curated colors, completeness arcs, etc.)
// lives in T-P0-485 (R02). R01 uses a simple working palette.

export interface PillarStyle {
  border: string;
  bg: string;
  name: string;
}

export const PILLAR_STYLES: Record<string, PillarStyle> = {
  pillar1: { border: "#475569", bg: "#f8fafc", name: "Coding & Algorithms" },
  pillar2: { border: "#d97706", bg: "#fffbeb", name: "ML Fundamentals & Theory" },
  pillar3: { border: "#059669", bg: "#ecfdf5", name: "ML System Design" },
  pillar4: { border: "#0284c7", bg: "#f0f9ff", name: "Applied ML & Domain-Specific" },
  pillar5: { border: "#7c3aed", bg: "#f5f3ff", name: "ML Infrastructure & MLOps" },
  pillar6: { border: "#e11d48", bg: "#fff1f2", name: "Deep Learning & LLM" },
  pillar7: { border: "#0d9488", bg: "#f0fdfa", name: "Math & Statistics" },
  pillar8: { border: "#ea580c", bg: "#fff7ed", name: "Behavioral & Leadership" },
};

const FALLBACK_STYLE: PillarStyle = {
  border: "#6b7280",
  bg: "#f9fafb",
  name: "Other",
};

export function styleForPillar(pillar: string | null | undefined): PillarStyle {
  if (!pillar) return FALLBACK_STYLE;
  return PILLAR_STYLES[pillar] ?? FALLBACK_STYLE;
}

export function colorForPillar(pillar: string | null | undefined): string {
  return styleForPillar(pillar).border;
}

export const LAYOUT_CONFIG = {
  rankSep: 150,
  nodeSep: 40,
  pillarColWidth: 260,
  categoryColWidth: 220,
  leafColWidth: 200,
  pillarNode: { width: 280, height: 60 },
  categoryNode: { width: 260, height: 54 },
  leafNode: { width: 240, height: 48 },
};

export const EDGE_STYLES = {
  parent: { stroke: "#cbd5e1", strokeWidth: 1.5 },
  canonical: { stroke: "#16a34a", strokeWidth: 2 },
  seeAlso: { stroke: "#0ea5e9", strokeWidth: 1 },
  drill: { stroke: "#8b5cf6", strokeWidth: 1 },
  other: { stroke: "#94a3b8", strokeWidth: 1 },
  dimmedOpacity: 0.3,
  fullOpacity: 1.0,
};
