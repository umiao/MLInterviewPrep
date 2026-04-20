import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import type { ReactNode } from "react";

interface SlideOverPanelProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  width?: string;
  /** Optional controls rendered between the title and the close button. */
  headerActions?: ReactNode;
  /** Optional extra classes on the header strip (e.g. orange top border for golden). */
  headerAccentClassName?: string;
}

/**
 * Default responsive max-width ladder for long-form drawers.
 * The drawer widens at lg/xl/2xl breakpoints so wider monitors get more
 * horizontal real estate. Prose width inside the drawer is capped
 * separately by DrawerLayout (default 680px) to preserve readability.
 */
export const DRAWER_RESPONSIVE_WIDTH =
  "max-w-xl md:max-w-2xl lg:max-w-4xl xl:max-w-5xl 2xl:max-w-6xl";

export default function SlideOverPanel({
  open,
  onClose,
  title,
  children,
  width = DRAWER_RESPONSIVE_WIDTH,
  headerActions,
  headerAccentClassName = "",
}: SlideOverPanelProps) {
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open, onClose]);

  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  if (!open) return null;

  return createPortal(
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 bg-black/40 transition-opacity"
      onClick={(e) => {
        if (e.target === overlayRef.current) onClose();
      }}
    >
      <div
        className={`fixed right-0 top-0 h-full bg-white shadow-xl w-full ${width} flex flex-col translate-x-0 opacity-100 transition-all duration-300 ease-in-out`}
        role="dialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
      >
        <div
          className={`flex items-center justify-between px-5 py-3 border-b border-gray-200 shrink-0 ${headerAccentClassName}`}
        >
          <h2 className="text-lg font-semibold text-gray-800 truncate pr-4">{title}</h2>
          <div className="flex items-center gap-2 shrink-0">
            {headerActions}
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-xl leading-none"
              aria-label="Close"
            >
              x
            </button>
          </div>
        </div>
        <div className="px-5 py-4 overflow-y-auto flex-1">{children}</div>
      </div>
    </div>,
    document.body,
  );
}
