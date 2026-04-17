interface HoverTooltipProps {
  title: string;
  pillarName: string;
  pillarColor: string;
  pillarBg: string;
  contentLength: number;
  edgeCount: number;
  actionHint: string;
}

const STUB_THRESHOLD = 2000;

function contentLabel(length: number): string {
  if (length === 0) return "Empty";
  if (length < STUB_THRESHOLD) return `Stub (${length.toLocaleString()} chars)`;
  return `${length.toLocaleString()} chars`;
}

/**
 * Floating informational tooltip rendered above a hovered KG node. Shown via
 * conditional render in each node component when its hovered flag is true.
 * Uses absolute positioning relative to the node wrapper so it tracks pan/zoom
 * naturally with no portal coordinate math.
 */
export function HoverTooltip({
  title,
  pillarName,
  pillarColor,
  pillarBg,
  contentLength,
  edgeCount,
  actionHint,
}: HoverTooltipProps) {
  return (
    <div
      data-testid="kg-tooltip"
      role="tooltip"
      className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 z-50 pointer-events-none"
      style={{ minWidth: 200 }}
    >
      <div className="rounded-md bg-gray-900 text-white shadow-lg px-3 py-2 text-[11px] leading-snug">
        <div className="font-semibold text-[12px] truncate">{title}</div>
        <div className="mt-1 flex items-center gap-1.5">
          <span
            className="inline-block rounded px-1.5 py-0.5 text-[10px] font-medium"
            style={{ backgroundColor: pillarBg, color: pillarColor }}
          >
            {pillarName}
          </span>
          <span className="text-gray-300">{contentLabel(contentLength)}</span>
        </div>
        {edgeCount > 0 && (
          <div className="mt-0.5 text-gray-400">
            {edgeCount} concept link{edgeCount === 1 ? "" : "s"}
          </div>
        )}
        <div className="mt-1 text-gray-400 italic">{actionHint}</div>
      </div>
    </div>
  );
}
