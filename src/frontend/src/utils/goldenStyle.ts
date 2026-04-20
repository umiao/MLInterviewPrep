/**
 * Shared visual tokens for the `is_golden` curation flag.
 *
 * `goldenCardClass` appends orange accent classes to a card's className when
 * the card is marked golden. Returns an empty string otherwise so callers can
 * concat without clobbering existing Tailwind classes.
 *
 * The matching `<GoldenBadge />` pill lives in `components/ui/GoldenBadge.tsx`
 * (split to keep this file JSX-free so react-refresh fast-reload still works).
 *
 * Pure utilities -- no consumers yet. T-GOLD-05 / T-GOLD-06 will wire them in.
 */

export function goldenCardClass(isGolden: boolean): string {
  if (!isGolden) return "";
  return "bg-orange-50 border-orange-300 border-l-4 border-l-orange-500";
}
