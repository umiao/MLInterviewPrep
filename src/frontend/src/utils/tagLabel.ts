/**
 * Convert a principle-tag slug or category label into a display label that the
 * browser can wrap on. CSS treats `_` as part of a word, so phrase-style slugs
 * like `problem_framing_before_persuasion` overflow narrow pills as a single
 * unbreakable token. Replacing `_` with a space restores natural break points.
 * The original slug stays in title= / aria-label= for hover and a11y.
 */
export function normalizeTagLabel(raw: string): string {
  return raw.replace(/_/g, " ");
}
