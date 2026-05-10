import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, ApiRequestError } from "../utils/api";
import type { CompanyDocument } from "../types/company";
import SlideOverPanel from "./ui/SlideOverPanel";
import MarkdownPreview from "./ui/MarkdownPreview";

export type CompanyDocDrawerStatus =
  | "loading"
  | "success"
  | "not_found"
  | "error";

interface CompanyDocDrawerProps {
  /** Company-document id to display. Null closes the drawer. */
  docId: number | null;
  onClose: () => void;
  /**
   * If a doc body contains `lc://N` links, this fires with the LC number.
   * Should set the OUTER drawer state (open ProblemDrawer); do NOT nest
   * inside this drawer.
   */
  onLcLinkClick?: (lcId: number) => void;
  /**
   * If a doc body contains `db://N` links, this fires with the problems-table
   * id. Same outer-drawer handling as `onLcLinkClick`.
   */
  onDbLinkClick?: (dbId: number) => void;
  /**
   * If a doc body contains `kg://N` links, this fires with the framework
   * node id. Bubbles to parent so it can navigate to /kg?node=nN -- do NOT
   * nest inside this drawer.
   */
  onKgLinkClick?: (kgId: number) => void;
}

interface CompanyDocDrawerBodyProps {
  docId: number | null;
  status: CompanyDocDrawerStatus;
  doc?: CompanyDocument;
  errorMessage?: string;
  onLcLinkClick?: (lcId: number) => void;
  onDbLinkClick?: (dbId: number) => void;
  onCdLinkClick?: (cdId: number) => void;
  onKgLinkClick?: (kgId: number) => void;
}

interface CompanyDocDrawerViewProps extends CompanyDocDrawerBodyProps {
  onClose: () => void;
}

/**
 * Format the warn-log message for a fetch failure. Extracted as a pure helper
 * so a vitest case can lock the prefix/shape without booting React.
 */
export function formatCompanyDocFetchWarning(
  docId: number,
  message: string,
): string {
  return `[CompanyDocDrawer] cd://${docId} fetch failed: ${message}`;
}

/**
 * Compute the drawer header title from the current fetch status. Pure
 * function so vitest can pin the title-by-status contract without needing
 * a DOM-capable environment for SlideOverPanel.
 */
export function companyDocDrawerTitle(
  status: CompanyDocDrawerStatus,
  docId: number | null,
  doc?: CompanyDocument,
): string {
  if (docId === null) return "";
  if (status === "success" && doc) return doc.title;
  if (status === "not_found") return "Document not found";
  if (status === "error") return "Failed to load document";
  return `Loading document (id=${docId})...`;
}

/**
 * Pure body renderer (no SlideOverPanel). The body is what tests assert
 * on -- SlideOverPanel uses createPortal(document.body, ...) which the
 * node-only vitest env cannot satisfy, so we keep the portal layer in
 * `CompanyDocDrawerView` and the renderable content here.
 */
export function CompanyDocDrawerBody({
  docId,
  status,
  doc,
  errorMessage,
  onLcLinkClick,
  onDbLinkClick,
  onCdLinkClick,
  onKgLinkClick,
}: CompanyDocDrawerBodyProps) {
  if (status === "loading") {
    return <div className="text-sm text-gray-400">Loading document...</div>;
  }
  if (status === "not_found") {
    return (
      <div className="text-sm text-red-600">
        Document not found (id={docId}). The link may be stale, or the doc
        was deleted -- check the source seed for the cd:// id.
      </div>
    );
  }
  if (status === "error") {
    return (
      <div className="text-sm text-red-600">
        Failed to load document: {errorMessage ?? "unknown error"}
      </div>
    );
  }
  if (status === "success" && doc) {
    return (
      <div className="space-y-5">
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {doc.is_golden && (
            <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-medium">
              Golden
            </span>
          )}
          {doc.doc_kind && (
            <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700">
              {doc.doc_kind}
            </span>
          )}
        </div>
        <section>
          {doc.content ? (
            <MarkdownPreview
              markdown={doc.content}
              onLcLinkClick={onLcLinkClick}
              onDbLinkClick={onDbLinkClick}
              onCdLinkClick={onCdLinkClick}
              onKgLinkClick={onKgLinkClick}
            />
          ) : (
            <p className="text-sm text-gray-400 italic">
              Document has no content yet.
            </p>
          )}
        </section>
      </div>
    );
  }
  return null;
}

/**
 * Presentation-only view. Wraps the pure body in SlideOverPanel; the
 * wrapper component below feeds it from useQuery state.
 */
export function CompanyDocDrawerView({
  docId,
  onClose,
  status,
  doc,
  errorMessage,
  onLcLinkClick,
  onDbLinkClick,
  onCdLinkClick,
  onKgLinkClick,
}: CompanyDocDrawerViewProps) {
  const open = docId !== null;
  const title = companyDocDrawerTitle(status, docId, doc);
  const accent =
    status === "success" && doc?.is_golden
      ? "border-t-4 border-amber-400"
      : "";

  return (
    <SlideOverPanel
      open={open}
      onClose={onClose}
      title={title}
      headerAccentClassName={accent}
    >
      <CompanyDocDrawerBody
        docId={docId}
        status={status}
        doc={doc}
        errorMessage={errorMessage}
        onLcLinkClick={onLcLinkClick}
        onDbLinkClick={onDbLinkClick}
        onCdLinkClick={onCdLinkClick}
        onKgLinkClick={onKgLinkClick}
      />
    </SlideOverPanel>
  );
}

/**
 * Right-side drawer that resolves `cd://N` against the
 * `GET /company-documents/{id}` endpoint.
 *
 * Per design review:
 *   1. Explicit 404 inline UI (not a blank panel, not a toast).
 *   2. console.warn on fetch failure for observability -- catches the kind of
 *      silent regression that produced T-P0-67x in the first place.
 *   3. Recursive cd:// inside the drawer REPLACES the active doc id
 *      (no history stack -- YAGNI). lc:// / db:// bubble up to the parent so
 *      they can swap to ProblemDrawer at the outer level rather than nesting.
 *
 * TODO: observe nested-drawer depth in usage; if multi-level navigation
 * appears, add a history stack here.
 */
export default function CompanyDocDrawer({
  docId,
  onClose,
  onLcLinkClick,
  onDbLinkClick,
  onKgLinkClick,
}: CompanyDocDrawerProps) {
  const [activeDocId, setActiveDocId] = useState<number | null>(docId);

  useEffect(() => {
    setActiveDocId(docId);
  }, [docId]);

  const open = activeDocId !== null;

  const { data, isLoading, isError, error } = useQuery<CompanyDocument>({
    queryKey: ["companyDoc", activeDocId],
    queryFn: () => api.get<CompanyDocument>(`/company-documents/${activeDocId}`),
    enabled: open,
    retry: false,
  });

  const errStatus =
    error instanceof ApiRequestError ? error.status : undefined;
  const errMessage =
    error instanceof Error ? error.message : error ? String(error) : "";

  useEffect(() => {
    if (isError && activeDocId !== null) {
      console.warn(formatCompanyDocFetchWarning(activeDocId, errMessage));
    }
  }, [isError, activeDocId, errMessage]);

  const status: CompanyDocDrawerStatus = !open
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
    <CompanyDocDrawerView
      docId={activeDocId}
      onClose={onClose}
      status={status}
      doc={data}
      errorMessage={errMessage}
      onLcLinkClick={onLcLinkClick}
      onDbLinkClick={onDbLinkClick}
      onCdLinkClick={(nextId) => setActiveDocId(nextId)}
      onKgLinkClick={onKgLinkClick}
    />
  );
}
