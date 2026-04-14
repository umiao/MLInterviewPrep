import { useRef, useState, useMemo, useCallback, useEffect } from "react";
import { useParams, Link, useNavigate, useSearchParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../utils/api";
import { usePrepNotes } from "../hooks/usePrepNotes";
import { useScrollRestore } from "../hooks/useScrollRestore";
import MarkdownPreview from "../components/ui/MarkdownPreview";
import ProblemDrawer from "../components/problems/ProblemDrawer";
import PrevNextNav from "../components/ui/PrevNextNav";
import ForumPostsTab from "../components/companies/ForumPostsTab";
import KnowledgeCardsPanel from "../components/companies/KnowledgeCardsPanel";
import DocTocSidebar from "../components/ui/DocTocSidebar";
import DynamicTocSidebar from "../components/ui/DynamicTocSidebar";
import type { TocHeading } from "../utils/slugify";
import {
  useCompanyDocuments,
  useUpdateDocument,
  type CompanyDocument,
} from "../hooks/useForumPosts";
import type { Company } from "../types/company";

type ImportMode = "append" | "replace";
/** "notes" = main prep_notes, "forum" = forum tab, "doc:N" = child document N */
type PageTab = "notes" | "forum" | "knowledge" | `doc:${number}`;

/** Threshold: only show TOC sidebar for documents >= 20K chars */
const TOC_MIN_CHARS = 8_000;

/**
 * Full-screen prep notes page at /companies/:companyId/prep.
 */
export default function PrepNotesPage() {
  const { companyId: rawId } = useParams<{ companyId: string }>();
  const companyId = Number(rawId);
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [importMode, setImportMode] = useState<ImportMode>("append");
  const [searchParams, setSearchParams] = useSearchParams();
  const initialDocParam = searchParams.get("doc");
  const [activeTab, setActiveTab] = useState<PageTab>(
    initialDocParam && /^\d+$/.test(initialDocParam)
      ? (`doc:${Number(initialDocParam)}` as PageTab)
      : "notes",
  );

  // Keep `?doc=N` URL param in sync with current activeTab.
  useEffect(() => {
    const next = new URLSearchParams(searchParams);
    if (typeof activeTab === "string" && activeTab.startsWith("doc:")) {
      next.set("doc", activeTab.slice(4));
    } else {
      next.delete("doc");
    }
    if (next.toString() !== searchParams.toString()) {
      setSearchParams(next, { replace: true });
    }
  }, [activeTab, searchParams, setSearchParams]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const captureScrollRef = useRef<(() => void) | null>(null);

  // scrollContainer via useState (not ref.current) for sidebar
  const [scrollContainer, setScrollContainer] = useState<HTMLElement | null>(null);

  // Dynamic TOC headings (for non-Adobe companies)
  const [tocHeadings, setTocHeadings] = useState<TocHeading[]>([]);
  const isAdobe = companyId === 23;

  // Callback ref to capture scroll container element via useState
  const scrollContainerRef = useCallback((node: HTMLDivElement | null) => {
    setScrollContainer(node);
    // Also set the contentRef for scroll restore compatibility
    (contentRef as React.MutableRefObject<HTMLDivElement | null>).current = node;
  }, []);

  const { data: company, isLoading } = useQuery<Company>({
    queryKey: ["companies", companyId],
    queryFn: () => api.get<Company>(`/companies/${companyId}`),
    enabled: companyId > 0,
  });

  // Fetch all companies for alphabetical prev/next navigation
  const { data: companies } = useQuery<Company[]>({
    queryKey: ["companies"],
    queryFn: () => api.get<Company[]>("/companies"),
    staleTime: 60_000,
  });

  const { prevCompany, nextCompany } = useMemo(() => {
    if (!companies?.length) return { prevCompany: null, nextCompany: null };
    const sorted = [...companies].sort((a, b) =>
      a.name.localeCompare(b.name),
    );
    const idx = sorted.findIndex((c) => c.id === companyId);
    return {
      prevCompany: idx > 0 ? sorted[idx - 1] : null,
      nextCompany: idx < sorted.length - 1 ? sorted[idx + 1] : null,
    };
  }, [companies, companyId]);

  const handleCompanyNav = useCallback(
    (id: number | string) => navigate(`/companies/${id}/prep`),
    [navigate],
  );

  const {
    notes,
    setNotes,
    mode,
    switchMode,
    saveStatus,
    setSaveStatus,
    handleRetry,
  } = usePrepNotes({
    companyId,
    initialNotes: company?.prep_notes ?? null,
    captureScrollRef,
  });

  const { captureScroll } = useScrollRestore(contentRef, textareaRef, mode);
  captureScrollRef.current = captureScroll;

  // Child documents
  const { data: documents } = useCompanyDocuments(companyId);

  // Parse active document ID from tab
  const activeDocId =
    typeof activeTab === "string" && activeTab.startsWith("doc:")
      ? Number(activeTab.slice(4))
      : null;

  /** Import .md file handler. */
  async function handleImport(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("mode", importMode);
      const res = await fetch(
        `/api/companies/${companyId}/prep-notes/import`,
        { method: "POST", body: formData },
      );
      if (!res.ok) {
        const detail = await res.json().catch(() => null);
        throw new Error(
          (detail as Record<string, string>)?.detail ?? res.statusText,
        );
      }
      const updated: Company = await res.json();
      const newNotes = updated.prep_notes ?? "";
      setNotes(newNotes);
      setSaveStatus("saved");
      queryClient.invalidateQueries({ queryKey: ["companies"] });
    } catch {
      setSaveStatus("error");
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        Loading...
      </div>
    );
  }

  if (!company) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <p className="text-gray-500">Company not found.</p>
        <Link to="/companies" className="text-blue-600 hover:text-blue-800 text-sm">
          Back to Companies
        </Link>
      </div>
    );
  }

  // Should we show TOC for the notes tab?
  const notesLargeEnough = (notes?.length ?? 0) >= TOC_MIN_CHARS;

  return (
    <div className="flex flex-col h-full">
      {/* Sticky header */}
      <header className="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shrink-0">
        <Link
          to="/companies"
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          &larr; Companies
        </Link>

        <div className="flex flex-col items-center gap-1">
          <div className="flex items-center gap-4">
            <h1 className="text-lg font-semibold text-gray-800">
              {company.name}
            </h1>
            <div className="flex gap-1 border border-gray-200 rounded p-0.5 items-center">
            <TabButton
              label="Notes"
              active={activeTab === "notes"}
              onClick={() => setActiveTab("notes")}
            />
            {documents && documents.length > 0 && (
              <select
                value={activeDocId !== null ? activeTab : ""}
                onChange={(e) => {
                  if (e.target.value) setActiveTab(e.target.value as PageTab);
                }}
                className={`text-sm px-3 py-1 rounded border-0 cursor-pointer ${
                  activeDocId !== null
                    ? "bg-gray-100 text-gray-800 font-medium"
                    : "text-gray-500 hover:bg-gray-50 bg-transparent"
                }`}
              >
                <option value="" disabled>
                  Documents ({documents.length})
                </option>
                {documents.map((doc) => (
                  <option key={doc.id} value={`doc:${doc.id}`}>
                    {doc.title}
                  </option>
                ))}
              </select>
            )}
            <TabButton
              label="Knowledge"
              active={activeTab === "knowledge"}
              onClick={() => setActiveTab("knowledge")}
            />
            <TabButton
              label="Forum Posts"
              active={activeTab === "forum"}
              onClick={() => setActiveTab("forum")}
            />
            </div>
          </div>
          {activeDocId !== null && documents && (
            <span className="text-xs text-gray-500">
              {documents.find((d) => d.id === activeDocId)?.title}
            </span>
          )}
        </div>

        <div className="flex items-center gap-3">
          <PrevNextNav
            prev={prevCompany ? { id: prevCompany.id, label: prevCompany.name } : null}
            next={nextCompany ? { id: nextCompany.id, label: nextCompany.name } : null}
            onNavigate={handleCompanyNav}
            enableKeyboard={mode === "preview"}
          />
          {/* Mode toggle -- notes/doc tabs only */}
          {(activeTab === "notes" || activeDocId !== null) && (
            <>
              <div className="flex gap-1">
                <button
                  onClick={() => switchMode("preview")}
                  className={`text-sm px-3 py-1.5 rounded ${
                    mode === "preview"
                      ? "bg-blue-100 text-blue-700 font-medium"
                      : "text-gray-500 hover:bg-gray-100"
                  }`}
                >
                  Preview
                </button>
                <button
                  onClick={() => switchMode("edit")}
                  className={`text-sm px-3 py-1.5 rounded ${
                    mode === "edit"
                      ? "bg-blue-100 text-blue-700 font-medium"
                      : "text-gray-500 hover:bg-gray-100"
                  }`}
                >
                  Edit
                </button>
              </div>

              {/* Save status */}
              <span className="text-sm min-w-[5rem] text-right">
                {saveStatus === "saving" && (
                  <span className="text-gray-400">Saving...</span>
                )}
                {saveStatus === "saved" && (
                  <span className="text-green-600">Saved</span>
                )}
                {saveStatus === "error" && (
                  <span className="text-red-600">
                    Failed{" "}
                    <button
                      onClick={handleRetry}
                      className="underline hover:text-red-800"
                    >
                      retry
                    </button>
                  </span>
                )}
              </span>
            </>
          )}
        </div>
      </header>

      {/* Content area */}
      {activeTab === "notes" ? (
        <>
          {/* TOC sidebar for large notes */}
          {mode === "preview" && notesLargeEnough && (
            isAdobe
              ? <DocTocSidebar scrollContainer={scrollContainer} />
              : <DynamicTocSidebar headings={tocHeadings} scrollContainer={scrollContainer} />
          )}
          <div ref={scrollContainerRef} className={`flex-1 overflow-auto p-6 flex flex-col min-h-0 ${mode === "preview" && notesLargeEnough ? "has-acronym-sidebar" : ""}`}>
            {mode === "edit" ? (
              <textarea
                ref={textareaRef}
                value={notes}
                onChange={(e) => {
                  setNotes(e.target.value);
                  if (saveStatus === "saved" || saveStatus === "error") {
                    setSaveStatus("idle");
                  }
                }}
                className="flex-1 min-h-0 w-full border border-gray-300 rounded px-4 py-3 text-base font-mono resize-none"
                placeholder="Write markdown prep notes here...&#10;&#10;- [ ] Review system design&#10;- [ ] Practice coding questions"
              />
            ) : (
              <div className="prep-prose">
                {notes ? (
                  <MarkdownPreview markdown={notes} onHeadingsExtracted={!isAdobe ? setTocHeadings : undefined} />
                ) : (
                  <p className="text-gray-400 italic">
                    No prep notes yet. Switch to Edit mode to add some.
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Import section */}
          <div className="border-t border-gray-200 px-6 py-3 bg-white shrink-0">
            <div className="flex items-center gap-3">
              <span className="text-xs font-medium text-gray-600">Import .md:</span>
              <label className="flex items-center gap-1 text-xs text-gray-500">
                <input
                  type="radio"
                  name="import-mode-page"
                  value="append"
                  checked={importMode === "append"}
                  onChange={() => setImportMode("append")}
                  className="w-3 h-3"
                />
                Append
              </label>
              <label className="flex items-center gap-1 text-xs text-gray-500">
                <input
                  type="radio"
                  name="import-mode-page"
                  value="replace"
                  checked={importMode === "replace"}
                  onChange={() => setImportMode("replace")}
                  className="w-3 h-3"
                />
                Replace
              </label>
              <input
                ref={fileInputRef}
                type="file"
                accept=".md,.markdown,.txt"
                onChange={handleImport}
                className="text-xs text-gray-500 file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:text-xs file:bg-blue-50 file:text-blue-700 file:cursor-pointer"
              />
            </div>
          </div>
        </>
      ) : activeTab === "knowledge" ? (
        <KnowledgeCardsPanel companyId={companyId} />
      ) : activeDocId !== null ? (
        <DocumentViewer
          companyId={companyId}
          docId={activeDocId}
          mode={mode}
        />
      ) : (
        <div className="flex-1 overflow-auto p-6 min-h-0">
          <ForumPostsTab companyId={companyId} />
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Sub-components                                                     */
/* ------------------------------------------------------------------ */

function TabButton({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`text-sm px-3 py-1 rounded whitespace-nowrap ${
        active
          ? "bg-gray-100 text-gray-800 font-medium"
          : "text-gray-500 hover:bg-gray-50"
      }`}
    >
      {label}
    </button>
  );
}

function DocumentViewer({
  companyId,
  docId,
  mode,
}: {
  companyId: number;
  docId: number;
  mode: "edit" | "preview";
}) {
  const { data: doc, isLoading } = useQuery<CompanyDocument>({
    queryKey: ["companyDocument", companyId, docId],
    queryFn: () =>
      api.get<CompanyDocument>(`/companies/${companyId}/documents/${docId}`),
    enabled: docId > 0,
  });
  const updateDoc = useUpdateDocument(companyId);
  const [localContent, setLocalContent] = useState<string | null>(null);
  const [scrollContainer, setScrollContainer] = useState<HTMLElement | null>(null);
  const [tocHeadings, setTocHeadings] = useState<TocHeading[]>([]);
  const [lcDrawerId, setLcDrawerId] = useState<number | null>(null);
  const [dbDrawerId, setDbDrawerId] = useState<number | null>(null);
  const isAdobe = companyId === 23;
  const contentRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollContainerRef = useCallback((node: HTMLDivElement | null) => {
    setScrollContainer(node);
    (contentRef as React.MutableRefObject<HTMLDivElement | null>).current = node;
  }, []);

  // Sync local state when doc loads or changes
  const content = localContent ?? doc?.content ?? "";
  const contentLargeEnough = content.length >= TOC_MIN_CHARS;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        Loading document...
      </div>
    );
  }
  if (!doc) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        Document not found.
      </div>
    );
  }

  const showSidebar = mode === "preview" && contentLargeEnough;

  return (
    <>
      {/* TOC sidebar for large documents */}
      {showSidebar && (
        isAdobe
          ? <DocTocSidebar scrollContainer={scrollContainer} />
          : <DynamicTocSidebar headings={tocHeadings} scrollContainer={scrollContainer} />
      )}
      <div ref={scrollContainerRef} className={`flex-1 overflow-auto p-6 flex flex-col min-h-0 ${showSidebar ? "has-acronym-sidebar" : ""}`}>
        {mode === "edit" ? (
          <textarea
            ref={textareaRef}
            value={content}
            onChange={(e) => setLocalContent(e.target.value)}
            onBlur={() => {
              if (localContent !== null && localContent !== doc.content) {
                updateDoc.mutate({ docId, content: localContent });
              }
            }}
            className="flex-1 min-h-0 w-full border border-gray-300 rounded px-4 py-3 text-base font-mono resize-none"
            placeholder="Document content..."
          />
        ) : (
          <div className="prep-prose">
            {content ? (
              <MarkdownPreview
                markdown={content}
                onHeadingsExtracted={!isAdobe ? setTocHeadings : undefined}
                onLcLinkClick={(id) => { setDbDrawerId(null); setLcDrawerId(id); }}
                onDbLinkClick={(id) => { setLcDrawerId(null); setDbDrawerId(id); }}
              />
            ) : (
              <p className="text-gray-400 italic">
                Empty document. Switch to Edit mode to add content.
              </p>
            )}
          </div>
        )}
      </div>
      <ProblemDrawer
        lcId={lcDrawerId}
        dbId={dbDrawerId}
        onClose={() => { setLcDrawerId(null); setDbDrawerId(null); }}
      />
    </>
  );
}
