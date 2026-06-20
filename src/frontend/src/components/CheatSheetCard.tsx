import { Link } from "react-router-dom";
import MarkdownPreview from "./ui/MarkdownPreview";
import type { SystemDesignCheatSheet } from "../types/system-design";

interface CheatSheetCardProps {
  /** The system-design row whose `cheat_sheet` one-pager is rendered. */
  item: SystemDesignCheatSheet;
  /** Short category label shown as a badge next to the title (e.g. "eBay"). */
  category: string;
}

/** Tailwind classes for the per-category badge, keyed by category label. */
const CATEGORY_BADGE_COLORS: Record<string, string> = {
  eBay: "bg-blue-100 text-blue-700",
  Pinterest: "bg-red-100 text-red-700",
  "ML MLSD": "bg-purple-100 text-purple-700",
  "ML Infra": "bg-indigo-100 text-indigo-700",
  Uber: "bg-gray-800 text-white",
  Generic: "bg-gray-100 text-gray-600",
};

/**
 * One-pager cheat-sheet card for a single system-design module.
 *
 * Renders a sticky title header (title + category badge + "Full design ->"
 * link) above the `cheat_sheet` markdown (KaTeX + GFM + ascii arch fences via
 * MarkdownPreview). The outer <section> carries `id={item.slug}` so the
 * Cheat Sheet tab's TOC sidebar and `?tab=cheatsheet#<slug>` deep links can
 * scroll to it. Falls back to a graceful empty state when `cheat_sheet` is null.
 */
export default function CheatSheetCard({ item, category }: CheatSheetCardProps) {
  const badgeColor =
    CATEGORY_BADGE_COLORS[category] ?? CATEGORY_BADGE_COLORS.Generic;

  return (
    <section
      id={item.slug}
      className="scroll-mt-6 bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden"
    >
      {/* Sticky header: title + category badge on the left, full-design link
          on the right. Stays pinned while scrolling through a long one-pager. */}
      <div className="sticky top-0 z-10 flex items-center justify-between gap-3 border-b border-gray-100 bg-white/95 px-5 py-3 backdrop-blur">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-800 min-w-0">
          <span className="truncate">{item.title}</span>
          <span
            className={`shrink-0 rounded px-2 py-0.5 text-xs font-medium ${badgeColor}`}
          >
            {category}
          </span>
        </h2>
        <Link
          to={`/system-design/${item.slug}`}
          className="shrink-0 text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline"
        >
          Full design -&gt;
        </Link>
      </div>

      <div className="px-5 py-4">
        {item.cheat_sheet ? (
          <MarkdownPreview markdown={item.cheat_sheet} />
        ) : (
          <p className="py-6 text-center text-sm text-gray-400">
            No cheat sheet yet
          </p>
        )}
      </div>
    </section>
  );
}
