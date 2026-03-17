import { useEffect, useCallback } from "react";

interface NavItem {
  id: number | string;
  label: string;
}

interface PrevNextNavProps {
  prev: NavItem | null;
  next: NavItem | null;
  onNavigate: (id: number | string) => void;
  /** Enable keyboard ArrowLeft/Right when no input is focused. Default true. */
  enableKeyboard?: boolean;
}

/**
 * Reusable prev/next chevron navigation with tooltips and keyboard support.
 * Arrows are disabled at boundaries. ArrowLeft/Right keys navigate when
 * no input/textarea/select is focused.
 */
export default function PrevNextNav({
  prev,
  next,
  onNavigate,
  enableKeyboard = true,
}: PrevNextNavProps) {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
      if ((e.target as HTMLElement)?.isContentEditable) return;

      if (e.key === "ArrowLeft" && prev) {
        e.preventDefault();
        onNavigate(prev.id);
      } else if (e.key === "ArrowRight" && next) {
        e.preventDefault();
        onNavigate(next.id);
      }
    },
    [prev, next, onNavigate],
  );

  useEffect(() => {
    if (!enableKeyboard) return;
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [enableKeyboard, handleKeyDown]);

  return (
    <div className="flex items-center gap-1">
      <button
        onClick={() => prev && onNavigate(prev.id)}
        disabled={!prev}
        className="px-2 py-1 text-sm rounded text-gray-500 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed"
        title={prev ? prev.label : "No previous"}
      >
        &#8592;
      </button>
      <button
        onClick={() => next && onNavigate(next.id)}
        disabled={!next}
        className="px-2 py-1 text-sm rounded text-gray-500 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed"
        title={next ? next.label : "No next"}
      >
        &#8594;
      </button>
    </div>
  );
}
