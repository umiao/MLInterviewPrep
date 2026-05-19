/**
 * Pure heading-extraction helpers for MarkdownPreview.
 *
 * Split out of MarkdownPreview.tsx so the component file exports only a
 * component (react-refresh/only-export-components) and so these pure
 * functions are unit-testable. See MarkdownPreview.headings.test.ts.
 *
 * SINGLE SOURCE OF TRUTH: both the TOC sidebar list AND the on-DOM
 * heading anchor `id` are derived from scanHeadings(markdown). Before
 * the L112 refactor, both came from childrenToText(renderedChildren) so
 * they matched each other (even when KaTeX made the slug garbage). The
 * naive refactor (sidebar from source, anchor still from childrenToText)
 * silently diverged for the 29 real math headings (e.g.
 * "复杂度推导：$O(n^2 d)$"): KaTeX renders an opaque MathML/HTML subtree
 * that childrenToText cannot reproduce from source. Re-coupling both
 * outputs to ONE pure scan makes them identical by construction for
 * math / inline-code / mixed-inline / duplicate headings alike, with no
 * render-phase ref mutation (react-hooks purity preserved).
 */
import { slugify, type TocHeading } from "../../utils/slugify";

/**
 * Collapse inline markdown in a heading's raw text to plain text.
 *
 * slugify() already strips * _ ~ ` # $ ( ) [ ] etc., so for realistic
 * headings the only load-bearing transforms are link/image unwrapping
 * (so a slug never includes a URL). Math delimiters are stripped; the
 * resulting LaTeX-ish source is slugified deterministically and -- key
 * point -- the SAME value is used for the anchor, so the sidebar link
 * always resolves even though the slug text itself is not pretty.
 * (Project policy is that KG headings should not contain formulas or
 * links; this keeps TOC correct until that content debt is cleaned.)
 */
export function headingPlainText(raw: string): string {
  return raw
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "") // image -> "" (no rendered text)
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1") // link -> its text
    .replace(/[*_~`]/g, "") // emphasis / strikethrough / inline code marks
    .replace(/\$+/g, "") // math delimiters
    .replace(/\s+/g, " ") // collapse internal whitespace (a  b -> a b)
    .trim();
}

export interface ScannedHeading extends TocHeading {
  /** 1-based source line of the ATX heading (matches hast position). */
  line: number;
}

/**
 * Scan markdown for ATX headings (levels 1-3 only, mirroring the old
 * h1/h2/h3-override collector), skipping fenced code blocks. Duplicate
 * slugs get GitHub-style `-1`, `-2`, ... suffixes; because this single
 * function feeds BOTH the sidebar and the anchor, the dedup is
 * automatically synchronized on both sides.
 */
export function scanHeadings(md: string): ScannedHeading[] {
  const out: ScannedHeading[] = [];
  const seen = new Map<string, number>();
  let inFence = false;
  const lines = md.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^\s*(```|~~~)/.test(line)) {
      inFence = !inFence;
      continue;
    }
    if (inFence) continue;
    const m = /^(#{1,3})\s+(.+?)\s*#*\s*$/.exec(line);
    if (!m) continue;
    const level = m[1].length;
    const text = headingPlainText(m[2]);
    const base = slugify(text);
    const n = seen.get(base) ?? 0;
    seen.set(base, n + 1);
    const id = n === 0 ? base : `${base}-${n}`;
    out.push({ level, text, id, line: i + 1 });
  }
  return out;
}

/** Sidebar/TOC view of the scan (drops the source line). */
export function extractHeadings(md: string): TocHeading[] {
  return scanHeadings(md).map(({ level, text, id }) => ({ level, text, id }));
}

/** Map 1-based source line -> heading id, for the on-DOM anchor. */
export function headingIdByLine(md: string): Map<number, string> {
  return new Map(scanHeadings(md).map((h) => [h.line, h.id]));
}
