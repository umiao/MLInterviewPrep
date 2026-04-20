/**
 * Tiny orange pill that signals a `is_golden` curated item. Sized to match the
 * FREQ_BADGE pill on MLFundamentals cards so the two can sit side-by-side
 * without visual clash. Renders nothing when `golden === false` so callers can
 * mount it unconditionally. Pairs with `goldenCardClass` in utils/goldenStyle.
 */

interface GoldenBadgeProps {
  golden: boolean;
  className?: string;
}

export default function GoldenBadge({
  golden,
  className = "",
}: GoldenBadgeProps) {
  if (!golden) return null;
  return (
    <span
      className={
        "inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full border uppercase tracking-wider bg-orange-50 text-orange-700 border-orange-200 " +
        className
      }
    >
      <svg
        viewBox="0 0 24 24"
        width="10"
        height="10"
        fill="currentColor"
        aria-hidden="true"
      >
        <path d="M12 2.5l2.9 6.3 6.9.7-5.2 4.7 1.5 6.8L12 17.7l-6.1 3.3 1.5-6.8L2.2 9.5l6.9-.7L12 2.5z" />
      </svg>
      <span>Golden</span>
    </span>
  );
}
