import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, ApiRequestError } from "../utils/api";
import type { SystemDesign, SystemDesignSection } from "../types/system-design";
import { SECTION_LABELS } from "../types/system-design";
import SlideOverPanel from "./ui/SlideOverPanel";
import MarkdownPreview from "./ui/MarkdownPreview";
import ImageLightbox from "./ui/ImageLightbox";

export type SystemDesignDrawerStatus =
  | "loading"
  | "success"
  | "not_found"
  | "error";

const SECTION_ORDER: SystemDesignSection[] = [
  "overview",
  "architecture",
  "dataflow",
  "formulas",
  "production_constraints",
  "tradeoffs",
  "defense",
  "verbal_outline",
  "cheat_sheet",
];

const EMPTY_SECTION_PLACEHOLDER = "尚未填写";

interface SystemDesignDrawerProps {
  /** System-design slug to display. Null closes the drawer. */
  slug: string | null;
  onClose: () => void;
  /**
   * Bubble lc:// links inside the drawer body up to the parent so it can
   * swap to ProblemDrawer at the outer level, NOT nest inside this drawer.
   */
  onLcLinkClick?: (lcId: number) => void;
  /** Same outer-drawer handling as `onLcLinkClick` for db://. */
  onDbLinkClick?: (dbId: number) => void;
  /** Same outer-drawer handling as `onLcLinkClick` for cd://. */
  onCdLinkClick?: (cdId: number) => void;
  /** Same outer-drawer handling as `onLcLinkClick` for kg:// (framework nodes). */
  onKgLinkClick?: (kgId: number) => void;
}

interface SystemDesignDrawerBodyProps {
  slug: string | null;
  status: SystemDesignDrawerStatus;
  design?: SystemDesign;
  errorMessage?: string;
  onLcLinkClick?: (lcId: number) => void;
  onDbLinkClick?: (dbId: number) => void;
  onCdLinkClick?: (cdId: number) => void;
  onSdLinkClick?: (slug: string) => void;
  onKgLinkClick?: (kgId: number) => void;
}

interface SystemDesignDrawerViewProps extends SystemDesignDrawerBodyProps {
  onClose: () => void;
}

/**
 * Format the warn-log message for a fetch failure. Extracted as a pure helper
 * so a vitest case can lock the prefix/shape without booting React.
 */
export function formatSystemDesignFetchWarning(
  slug: string,
  message: string,
): string {
  return `[SystemDesignDrawer] sd://${slug} fetch failed: ${message}`;
}

/**
 * Compute the drawer header title from the current fetch status. Pure
 * function so vitest can pin the title-by-status contract without needing
 * a DOM-capable environment for SlideOverPanel.
 */
export function systemDesignDrawerTitle(
  status: SystemDesignDrawerStatus,
  slug: string | null,
  design?: SystemDesign,
): string {
  if (slug === null) return "";
  if (status === "success" && design) return design.title;
  if (status === "not_found") return "Module not found";
  if (status === "error") return "Failed to load module";
  return `Loading system design (slug=${slug})...`;
}

/**
 * Pure body renderer (no SlideOverPanel). Mirrors CompanyDocDrawerBody --
 * SlideOverPanel uses createPortal which the node-only vitest env cannot
 * satisfy, so the renderable content lives here and the portal layer in
 * `SystemDesignDrawerView`.
 */
export function SystemDesignDrawerBody({
  slug,
  status,
  design,
  errorMessage,
  onLcLinkClick,
  onDbLinkClick,
  onCdLinkClick,
  onSdLinkClick,
  onKgLinkClick,
}: SystemDesignDrawerBodyProps) {
  if (status === "loading") {
    return (
      <div className="text-sm text-gray-400">Loading system design...</div>
    );
  }
  if (status === "not_found") {
    return (
      <div className="text-sm text-red-600">
        System design module not found (slug={slug}). Link may be stale or
        the module was renamed -- check system_designs.slug.
      </div>
    );
  }
  if (status === "error") {
    return (
      <div className="text-sm text-red-600">
        Failed to load: {errorMessage ?? "unknown error"}
      </div>
    );
  }
  if (status === "success" && design) {
    return (
      <div className="space-y-6">
        {SECTION_ORDER.map((section) => {
          const content = design[section];
          return (
            <section key={section}>
              <h3 className="text-base font-semibold text-gray-800 mb-2">
                {SECTION_LABELS[section]}
              </h3>
              {section === "architecture" && design.diagram_filename && (
                <ImageLightbox
                  src={`/static/system-designs/${design.diagram_filename}`}
                  className="w-full max-h-96 object-contain mb-4 rounded border"
                  alt={`${design.title} architecture diagram`}
                />
              )}
              {content ? (
                <MarkdownPreview
                  markdown={content}
                  onLcLinkClick={onLcLinkClick}
                  onDbLinkClick={onDbLinkClick}
                  onCdLinkClick={onCdLinkClick}
                  onSdLinkClick={onSdLinkClick}
                  onKgLinkClick={onKgLinkClick}
                />
              ) : (
                <p className="text-sm text-gray-400 italic">
                  {EMPTY_SECTION_PLACEHOLDER}
                </p>
              )}
            </section>
          );
        })}
      </div>
    );
  }
  return null;
}

/**
 * Presentation-only view. Wraps the pure body in SlideOverPanel; the
 * wrapper component below feeds it from useQuery state.
 */
export function SystemDesignDrawerView({
  slug,
  onClose,
  status,
  design,
  errorMessage,
  onLcLinkClick,
  onDbLinkClick,
  onCdLinkClick,
  onSdLinkClick,
  onKgLinkClick,
}: SystemDesignDrawerViewProps) {
  const open = slug !== null;
  const title = systemDesignDrawerTitle(status, slug, design);

  return (
    <SlideOverPanel open={open} onClose={onClose} title={title}>
      <SystemDesignDrawerBody
        slug={slug}
        status={status}
        design={design}
        errorMessage={errorMessage}
        onLcLinkClick={onLcLinkClick}
        onDbLinkClick={onDbLinkClick}
        onCdLinkClick={onCdLinkClick}
        onSdLinkClick={onSdLinkClick}
        onKgLinkClick={onKgLinkClick}
      />
    </SlideOverPanel>
  );
}

/**
 * Right-side drawer that resolves `sd://<slug>` against the
 * `GET /system-designs/{slug}` endpoint.
 *
 * Mirrors CompanyDocDrawer (T-P0-673):
 *   1. Explicit 404 inline UI (not a blank panel, not a toast).
 *   2. console.warn on fetch failure for observability.
 *   3. Recursive sd:// inside the drawer REPLACES the active slug
 *      (no history stack -- YAGNI). lc:// / db:// / cd:// bubble up to the
 *      parent so they can swap to ProblemDrawer / CompanyDocDrawer at the
 *      outer level rather than nesting.
 *
 * TODO: observe nested-drawer depth in usage; if multi-level navigation
 * appears, add a history stack here.
 */
export default function SystemDesignDrawer({
  slug,
  onClose,
  onLcLinkClick,
  onDbLinkClick,
  onCdLinkClick,
  onKgLinkClick,
}: SystemDesignDrawerProps) {
  const [activeSlug, setActiveSlug] = useState<string | null>(slug);

  useEffect(() => {
    setActiveSlug(slug);
  }, [slug]);

  const open = activeSlug !== null;

  const { data, isLoading, isError, error } = useQuery<SystemDesign>({
    queryKey: ["system-design", activeSlug],
    queryFn: () => api.get<SystemDesign>(`/system-designs/${activeSlug}`),
    enabled: open,
    retry: false,
  });

  const errStatus =
    error instanceof ApiRequestError ? error.status : undefined;
  const errMessage =
    error instanceof Error ? error.message : error ? String(error) : "";

  useEffect(() => {
    if (isError && activeSlug !== null) {
      console.warn(formatSystemDesignFetchWarning(activeSlug, errMessage));
    }
  }, [isError, activeSlug, errMessage]);

  const status: SystemDesignDrawerStatus = !open
    ? "loading"
    : isLoading
      ? "loading"
      : isError
        ? errStatus === 404
          ? "not_found"
          : "error"
        : data
          ? "success"
          : "loading";

  return (
    <SystemDesignDrawerView
      slug={activeSlug}
      onClose={onClose}
      status={status}
      design={data}
      errorMessage={errMessage}
      onLcLinkClick={onLcLinkClick}
      onDbLinkClick={onDbLinkClick}
      onCdLinkClick={onCdLinkClick}
      onSdLinkClick={(nextSlug) => setActiveSlug(nextSlug)}
      onKgLinkClick={onKgLinkClick}
    />
  );
}
