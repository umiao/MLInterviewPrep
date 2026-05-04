/**
 * Shared visual tokens for curation flags on problem cards.
 *
 * `goldenCardClass` appends orange accent classes when a card is marked
 * golden (`is_golden=1` curation flag). `referenceCardClass` is the parallel
 * purple/indigo treatment for "reference" cards -- e.g. the ML Naive
 * Reference summary card on QuickIndex (KNN + KMeans + LogReg side-by-side
 * impls). Both return an empty string when the flag is false so callers can
 * concat without clobbering existing Tailwind classes.
 *
 * The matching `<GoldenBadge />` pill lives in `components/ui/GoldenBadge.tsx`
 * (split to keep this file JSX-free so react-refresh fast-reload still works).
 */

export function goldenCardClass(isGolden: boolean): string {
  if (!isGolden) return "";
  return "bg-orange-50 border-orange-300 border-l-4 border-l-orange-500";
}

export function referenceCardClass(isReference: boolean): string {
  if (!isReference) return "";
  return "bg-purple-50 border-purple-300 border-l-4 border-l-purple-500";
}
