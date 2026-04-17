// Shared completeness indicator used by LeafNode and leaf-like CategoryNode
// (0-children categories). Outline ring with arc fill; filled disc with
// checkmark when fraction >= 1.

export const COMPLETENESS_FULL = 10000;
export const STUB_THRESHOLD = 2000;

interface CompletenessArcProps {
  fraction: number;
  color: string;
}

export function CompletenessArc({ fraction, color }: CompletenessArcProps) {
  const size = 14;
  const r = 5;
  const cx = size / 2;
  const cy = size / 2;
  const circumference = 2 * Math.PI * r;
  const clamped = Math.max(0, Math.min(1, fraction));
  if (clamped >= 1) {
    return (
      <svg width={size} height={size} aria-hidden>
        <circle cx={cx} cy={cy} r={r} fill={color} />
        <path
          d={`M${cx - 2.2} ${cy + 0.2} L${cx - 0.6} ${cy + 1.8} L${cx + 2.4} ${cy - 1.6}`}
          stroke="white"
          strokeWidth={1.4}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );
  }
  return (
    <svg width={size} height={size} aria-hidden>
      <circle
        cx={cx}
        cy={cy}
        r={r}
        fill="none"
        stroke="#e2e8f0"
        strokeWidth={1.5}
      />
      {clamped > 0 && (
        <circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={1.5}
          strokeDasharray={`${circumference * clamped} ${circumference}`}
          transform={`rotate(-90 ${cx} ${cy})`}
          strokeLinecap="round"
        />
      )}
    </svg>
  );
}

interface StubBadgeProps {
  className?: string;
}

export function StubBadge({ className = "" }: StubBadgeProps) {
  return (
    <span
      data-testid="kg-stub-badge"
      className={`text-[9px] leading-none px-1 py-0.5 rounded bg-gray-200 text-gray-600 font-medium uppercase tracking-wide ${className}`}
    >
      stub
    </span>
  );
}
