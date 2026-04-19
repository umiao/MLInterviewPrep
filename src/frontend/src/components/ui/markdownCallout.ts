// Callout contract locked by T-P0-514. Drawer markdown blockquotes that
// open with one of these literal prefixes render as styled callouts. All
// other blockquotes fall back to the default blockquote style.
//
// Examples (exact literal match required, leading bold tags only):
//   > **GOOD**: ...
//   > **BAD**: ...
//   > **NOTE**: ...

export type CalloutKind = "good" | "bad" | "note";

const CALLOUT_PREFIX_RE = /^\s*\*\*(GOOD|BAD|NOTE)\*\*\s*:/;
const CALLOUT_LABEL_RE = /^(GOOD|BAD|NOTE)$/;

// Source-text matcher (raw markdown, before bold parsing). Currently only
// used by unit tests; the runtime path uses getCalloutKindFromHast.
export function getCalloutKind(leadingText: string): CalloutKind | null {
  const m = CALLOUT_PREFIX_RE.exec(leadingText);
  if (!m) return null;
  return m[1].toLowerCase() as CalloutKind;
}

// Minimal hast subset we read. Real hast nodes carry many more fields, but
// the override only needs tagName/value/children to walk the prefix.
export interface HastLike {
  type?: string;
  tagName?: string;
  value?: string;
  children?: HastLike[];
}

// Hast-AST matcher used by the react-markdown blockquote override. By the
// time the override runs, markdown bold has already been parsed to a
// <strong> element, so a string regex on rendered text cannot tell a bold
// "**GOOD**:" from a plain "GOOD:". Walking the AST preserves the bold
// requirement that distinguishes a callout from an ordinary blockquote.
export function getCalloutKindFromHast(node: HastLike | undefined): CalloutKind | null {
  if (!node || !Array.isArray(node.children)) return null;
  // Skip leading whitespace text nodes inside the blockquote
  const firstElement = node.children.find(
    (c) => c.type === "element" || (c.type === "text" && c.value && c.value.trim() !== ""),
  );
  if (!firstElement || firstElement.tagName !== "p" || !Array.isArray(firstElement.children)) {
    return null;
  }
  const para = firstElement.children;
  if (para.length === 0) return null;
  // First child of the paragraph must be a <strong> with text GOOD/BAD/NOTE
  const strong = para[0];
  if (strong.tagName !== "strong" || !Array.isArray(strong.children)) return null;
  const strongText = strong.children
    .filter((c) => c.type === "text" && typeof c.value === "string")
    .map((c) => c.value as string)
    .join("");
  const labelMatch = CALLOUT_LABEL_RE.exec(strongText);
  if (!labelMatch) return null;
  // The next sibling must be a text node starting with ":" (after optional space)
  const next = para[1];
  if (!next || next.type !== "text" || typeof next.value !== "string") return null;
  if (!/^\s*:/.test(next.value)) return null;
  return labelMatch[1].toLowerCase() as CalloutKind;
}

export function calloutClass(kind: CalloutKind): string {
  return `callout callout-${kind}`;
}
