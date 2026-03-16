/**
 * Markdown checkbox utilities for prep notes.
 */

const UNCHECKED_RE = /^[-*]\s*\[ \]/;
const CHECKED_RE = /^[-*]\s*\[[xX]\]/;

/**
 * Count unchecked checkboxes (- [ ] or * [ ]) in markdown text.
 */
export function countUnchecked(md: string | null | undefined): number {
  if (!md) return 0;
  return md.split("\n").filter((line) => UNCHECKED_RE.test(line.trimStart())).length;
}

/**
 * Count checked checkboxes (- [x] or * [x]) in markdown text.
 */
export function countChecked(md: string | null | undefined): number {
  if (!md) return 0;
  return md.split("\n").filter((line) => CHECKED_RE.test(line.trimStart())).length;
}

/**
 * Toggle the checkbox on a specific line index (0-based).
 * Returns the updated markdown string.
 */
export function toggleCheckbox(md: string, lineIndex: number): string {
  const lines = md.split("\n");
  if (lineIndex < 0 || lineIndex >= lines.length) return md;

  const line = lines[lineIndex];
  if (UNCHECKED_RE.test(line.trimStart())) {
    lines[lineIndex] = line.replace("[ ]", "[x]");
  } else if (CHECKED_RE.test(line.trimStart())) {
    lines[lineIndex] = line.replace(/\[[xX]\]/, "[ ]");
  }

  return lines.join("\n");
}
