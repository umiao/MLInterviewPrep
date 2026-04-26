/**
 * Tiny purple pill that signals a `is_signature` story. Distinct from
 * GoldenBadge (which marks quality / curated items) -- Signature marks the
 * single proudest-impact story that should be reached for in open-ended
 * "biggest impact" questions. Renders nothing when `signature === false`.
 */

interface SignatureBadgeProps {
  signature: boolean;
  className?: string;
}

export default function SignatureBadge({
  signature,
  className = "",
}: SignatureBadgeProps) {
  if (!signature) return null;
  return (
    <span
      title="Signature Story -- proudest achievement, use for open-ended impact questions"
      className={
        "inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full border uppercase tracking-wider bg-purple-50 text-purple-700 border-purple-200 " +
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
        <path d="M12 2l2.39 7.36H22l-6.18 4.49L18.21 21 12 16.51 5.79 21l2.39-7.15L2 9.36h7.61L12 2z" />
      </svg>
      <span>Signature</span>
    </span>
  );
}
