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
  "ml-fundamentals": {
    border: "#0891b2",
    bg: "#ecfeff",
    name: "ML 八股文 · Fundamentals",
  },
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

export interface StyleOptions {
  // When true, returns the muted (30% over white) variant of the pillar
  // background. Used by collapsed category nodes so the canvas shows an
  // at-a-glance saturation contrast between expanded and collapsed state
  // (KG-UX-15). Color is the dual-channel companion to border thickness +
  // chevron so color-blind users still see the distinction.
  collapsed?: boolean;
}

// Blend a #rrggbb hex color with white at the given opacity. Returns #rrggbb.
// Falls back to the input string if the format is unrecognised.
function mutedBgVariant(hex: string, alpha = 0.3): string {
  const m = hex.match(/^#([0-9a-fA-F]{6})$/);
  if (!m) return hex;
  const int = parseInt(m[1], 16);
  const r = (int >> 16) & 0xff;
  const g = (int >> 8) & 0xff;
  const b = int & 0xff;
  const mix = (channel: number) =>
    Math.round(alpha * channel + (1 - alpha) * 255);
  const rr = mix(r).toString(16).padStart(2, "0");
  const gg = mix(g).toString(16).padStart(2, "0");
  const bb = mix(b).toString(16).padStart(2, "0");
  return `#${rr}${gg}${bb}`;
}

export function styleForPillar(
  pillar: string | null | undefined,
  options?: StyleOptions,
): PillarStyle {
  const base = pillar
    ? (PILLAR_STYLES[pillar] ?? FALLBACK_STYLE)
    : FALLBACK_STYLE;
  if (options?.collapsed) {
    return { ...base, bg: mutedBgVariant(base.bg) };
  }
  return base;
}

export function colorForPillar(pillar: string | null | undefined): string {
  return styleForPillar(pillar).border;
}

export const LAYOUT_CONFIG = {
  rankSep: 180,
  nodeSep: 20,
  pillarColWidth: 260,
  categoryColWidth: 220,
  leafColWidth: 200,
  pillarNode: { width: 280, height: 60 },
  categoryNode: { width: 260, height: 54 },
  leafNode: { width: 240, height: 48 },
  laneGap: 60,
};

export const LANE_SEPARATOR_STYLE = {
  color: "#e2e8f0",
  widthPx: 1,
  dash: "6 4",
};

export const EDGE_STYLES = {
  // Parent edges are pillar-colored at runtime; these are fallback values.
  parent: { stroke: "#cbd5e1", strokeWidth: 2, opacity: 0.7 },
  canonical: { stroke: "#16a34a", strokeWidth: 2 },
  seeAlso: { stroke: "#0ea5e9", strokeWidth: 1 },
  drill: { stroke: "#8b5cf6", strokeWidth: 1 },
  other: { stroke: "#94a3b8", strokeWidth: 1 },
  dimmedOpacity: 0.3,
  fullOpacity: 1.0,
};
