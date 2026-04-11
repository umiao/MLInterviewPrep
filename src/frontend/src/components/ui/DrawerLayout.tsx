import type { ReactNode } from "react";

export type DrawerLayoutVariant = "two-column" | "single-column";

interface DrawerLayoutProps {
  left: ReactNode;
  right: ReactNode;
  variant?: DrawerLayoutVariant;
  leftWidth?: string;
  proseMaxWidth?: string;
}

/**
 * Single source of truth for the responsive drawer layout used by long-form
 * drawers (behavioral example drawer, prep notes drawer, etc.).
 *
 * variant="two-column" (default): below lg the layout stacks vertically
 * (left pane first, then right pane). From lg and up the left pane becomes
 * a sticky sidebar and the right pane takes the remaining width with a
 * prose cap so text stays readable no matter how wide the drawer grows.
 *
 * variant="single-column": always stacked, never two-column. Use for
 * short-form drawers where a meta sidebar would look silly.
 */
export default function DrawerLayout({
  left,
  right,
  variant = "two-column",
  leftWidth = "w-72",
  proseMaxWidth = "max-w-[680px]",
}: DrawerLayoutProps) {
  if (variant === "single-column") {
    return (
      <div
        data-drawer-layout="single-column"
        className="flex flex-col gap-4"
      >
        {left != null && (
          <div data-drawer-pane="left" className="shrink-0">
            {left}
          </div>
        )}
        <div data-drawer-pane="right" className="min-w-0">
          <div className={`${proseMaxWidth} w-full`}>{right}</div>
        </div>
      </div>
    );
  }

  return (
    <div
      data-drawer-layout="two-column"
      className="flex flex-col lg:flex-row lg:items-start lg:gap-6"
    >
      <aside
        data-drawer-pane="left"
        className={`${leftWidth} shrink-0 mb-4 lg:mb-0 lg:sticky lg:top-0 lg:self-start lg:max-h-[calc(100vh-8rem)] lg:overflow-y-auto`}
      >
        {left}
      </aside>
      <div data-drawer-pane="right" className="flex-1 min-w-0">
        <div className={`${proseMaxWidth} w-full`}>{right}</div>
      </div>
    </div>
  );
}
