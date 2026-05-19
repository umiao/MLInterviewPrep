import { useEffect, useMemo, useRef } from "react";
import type { Element, ElementContent } from "hast";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeRaw from "rehype-raw";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import "katex/dist/katex.min.css";
import { slugify, type TocHeading } from "../../utils/slugify";
import { extractHeadings, headingIdByLine } from "./markdownHeadings";
import { calloutClass, getCalloutKindFromHast, type HastLike } from "./markdownCallout";

interface MarkdownPreviewProps {
  markdown: string;
  onCheckboxClick?: (lineIndex: number) => void;
  onHeadingsExtracted?: (headings: TocHeading[]) => void;
  /**
   * Called when the user clicks a link with href of form `lc://N` (e.g. `lc://332`).
   * When provided, those links render as buttons that invoke this handler with the
   * LeetCode number instead of navigating. All other links behave normally.
   */
  onLcLinkClick?: (lcId: number) => void;
  /**
   * Called when the user clicks a link with href of form `db://N` (e.g. `db://1074`).
   * When provided, those links render as buttons invoking this handler with the
   * problems-table database id (for custom problems with no LC number).
   */
  onDbLinkClick?: (dbId: number) => void;
  /**
   * Called when the user clicks a link with href of form `cd://N` (e.g. `cd://87`).
   * When provided, those links render as buttons invoking this handler with the
   * company-document id, opening the company-doc drawer.
   */
  onCdLinkClick?: (cdId: number) => void;
  /**
   * Called when the user clicks a link with href of form `sd://<slug>` (e.g.
   * `sd://pinterest-ad-ctr`). When provided, those links render as buttons
   * invoking this handler with the system-design slug, opening the system-design
   * drawer. Slugs are lowercase kebab-case per the `system_designs` table.
   */
  onSdLinkClick?: (slug: string) => void;
  /**
   * Called when the user clicks a link with href of form `kg://N` (e.g.
   * `kg://7`). N is the framework_nodes.id. When provided, those links render
   * as buttons invoking this handler with the node id, typically dispatched
   * to navigate to `/kg?node=nN` or open a node drawer.
   */
  onKgLinkClick?: (nodeId: number) => void;
}

/** Green checkmark SVG (GitHub PR style). */
function CheckIcon() {
  return (
    <svg className="w-4 h-4 text-green-600 shrink-0 mt-0.5" viewBox="0 0 16 16" fill="currentColor">
      <path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.75.75 0 0 1 1.06-1.06L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z" />
    </svg>
  );
}

/** Gray circle (unchecked). */
function UncheckedIcon() {
  return (
    <svg className="w-4 h-4 text-gray-300 shrink-0 mt-0.5" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="8" cy="8" r="6" />
    </svg>
  );
}

/** Extract plain text from React children (strips nested elements). */
function childrenToText(children: React.ReactNode): string {
  if (typeof children === "string") return children;
  if (typeof children === "number") return String(children);
  if (Array.isArray(children)) return children.map(childrenToText).join("");
  if (children && typeof children === "object" && "props" in children) {
    const el = children as React.ReactElement<{ children?: React.ReactNode }>;
    return childrenToText(el.props.children);
  }
  return "";
}

/**
 * Renders markdown with GFM support (tables, strikethrough, task lists)
 * and consistent checkbox icons (GitHub PR style).
 *
 * When onHeadingsExtracted is provided, emits heading metadata after render
 * so a TOC sidebar can consume it (single data source pattern).
 */
export default function MarkdownPreview({
  markdown,
  onCheckboxClick,
  onHeadingsExtracted,
  onLcLinkClick,
  onDbLinkClick,
  onCdLinkClick,
  onSdLinkClick,
  onKgLinkClick,
}: MarkdownPreviewProps) {
  // Headings are a pure function of the source -> derive, don't collect.
  // (Was: reset + push into a ref during render -- a react-hooks render
  // purity violation, fragile under StrictMode / the React Compiler.)
  const headings = useMemo(() => extractHeadings(markdown), [markdown]);
  // Same single source feeds the on-DOM anchor id (keyed by the hast
  // node's source line) so sidebar id === anchor id by construction --
  // incl. math / duplicate / mixed-inline headings.
  const idByLine = useMemo(() => headingIdByLine(markdown), [markdown]);
  const prevJsonRef = useRef<string>("");

  // Emit when the derived headings change. prevJsonRef is written ONLY
  // inside the effect (allowed -- not during render) to dedupe identical
  // emissions when the parent passes a fresh onHeadingsExtracted lambda.
  useEffect(() => {
    if (!onHeadingsExtracted) return;
    const json = JSON.stringify(headings);
    if (json !== prevJsonRef.current) {
      prevJsonRef.current = json;
      onHeadingsExtracted(headings);
    }
  }, [headings, onHeadingsExtracted]);

  /**
   * Heading component: sets the on-DOM anchor `id` from the SAME
   * scanHeadings() pass that builds the sidebar (looked up by the hast
   * node's source line), so the two can never diverge -- including for
   * math/duplicate headings KaTeX would otherwise garble. Falls back to
   * slugify(childrenToText(children)) only if position is unavailable
   * (defensive; react-markdown supplies it for ATX headings).
   */
  function HeadingWithId({ level, node, children, ...props }: {
    level: number;
    node?: Element;
    children?: React.ReactNode;
  } & React.HTMLAttributes<HTMLHeadingElement>) {
    const line = node?.position?.start?.line;
    const id =
      (line != null ? idByLine.get(line) : undefined) ??
      slugify(childrenToText(children));
    if (level === 1) return <h1 id={id} {...props}>{children}</h1>;
    if (level === 2) return <h2 id={id} {...props}>{children}</h2>;
    return <h3 id={id} {...props}>{children}</h3>;
  }

  return (
    <div className="prose prose-sm max-w-none
      prose-table:border-collapse prose-table:w-full
      prose-th:border prose-th:border-gray-300 prose-th:bg-gray-50 prose-th:px-3 prose-th:py-2 prose-th:text-left prose-th:text-xs prose-th:font-semibold prose-th:text-gray-600
      prose-td:border prose-td:border-gray-200 prose-td:px-3 prose-td:py-2 prose-td:text-sm
      prose-tr:even:bg-gray-50
      prose-code:bg-gray-100 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:before:content-none prose-code:after:content-none
      prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-pre:rounded-lg prose-pre:p-4
      prose-a:text-blue-600 prose-a:no-underline hover:prose-a:underline
      prose-headings:text-gray-900
      prose-strong:text-gray-900
    ">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, [remarkMath, { singleDollarTextMath: true }]]}
        rehypePlugins={[rehypeRaw, rehypeKatex]}
        urlTransform={(url) => url}
        components={{
          a: ({ href, children, ...rest }) => {
            // `lc://332` -> drawer click. `db://1074` -> drawer by DB id. Everything else -> default anchor.
            const lcMatch = typeof href === "string" ? href.match(/^lc:\/\/(\d+)$/) : null;
            if (lcMatch && onLcLinkClick) {
              const lcId = Number(lcMatch[1]);
              return (
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    onLcLinkClick(lcId);
                  }}
                  className="text-blue-600 underline hover:text-blue-800 bg-transparent border-0 p-0 cursor-pointer font-inherit"
                >
                  {children}
                </button>
              );
            }
            // `db://N` opens the doc drawer. `db://N#anchor` also opens the
            // drawer (anchor ignored at link layer for now; future task adds
            // scroll-to-anchor inside SlideOverPanel). Without this optional
            // suffix, anchor-bearing deep-links would fall through to a broken
            // <a href="db://N#anchor" target="_blank"> new-tab.
            const dbMatch = typeof href === "string" ? href.match(/^db:\/\/(\d+)(?:#[^\s]*)?$/) : null;
            if (dbMatch && onDbLinkClick) {
              const dbId = Number(dbMatch[1]);
              return (
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    onDbLinkClick(dbId);
                  }}
                  className="text-blue-600 underline hover:text-blue-800 bg-transparent border-0 p-0 cursor-pointer font-inherit"
                >
                  {children}
                </button>
              );
            }
            // `cd://N` opens the company-document drawer (peer to db:// for
            // problems). Optional `#anchor` suffix is accepted but ignored at
            // the link layer (anchor-scroll inside drawer is a future task).
            const cdMatch = typeof href === "string" ? href.match(/^cd:\/\/(\d+)(?:#[^\s]*)?$/) : null;
            if (cdMatch && onCdLinkClick) {
              const cdId = Number(cdMatch[1]);
              return (
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    onCdLinkClick(cdId);
                  }}
                  className="text-blue-600 underline hover:text-blue-800 bg-transparent border-0 p-0 cursor-pointer font-inherit"
                >
                  {children}
                </button>
              );
            }
            // `sd://<slug>` opens the system-design drawer. Slug is lowercase
            // kebab-case per system_designs table (case-strict so we don't
            // silently accept malformed links). Optional `#anchor` accepted
            // but ignored at the link layer.
            const sdMatch = typeof href === "string" ? href.match(/^sd:\/\/([a-z0-9-]+)(?:#[^\s]*)?$/) : null;
            if (sdMatch && onSdLinkClick) {
              const slug = sdMatch[1];
              return (
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    onSdLinkClick(slug);
                  }}
                  className="text-blue-600 underline hover:text-blue-800 bg-transparent border-0 p-0 cursor-pointer font-inherit"
                >
                  {children}
                </button>
              );
            }
            // `kg://N` opens (or navigates to) the framework_nodes node id N
            // -- peer to db:// / cd:// for problems / company-docs. The
            // dispatcher (provided by the consumer) typically navigates to
            // /kg?node=nN; the URL state hook there auto-expands ancestors and
            // focuses the canvas. Optional `#anchor` suffix is accepted but
            // ignored at the link layer.
            const kgMatch = typeof href === "string" ? href.match(/^kg:\/\/(\d+)(?:#[^\s]*)?$/) : null;
            if (kgMatch && onKgLinkClick) {
              const kgId = Number(kgMatch[1]);
              return (
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    onKgLinkClick(kgId);
                  }}
                  className="text-blue-600 underline hover:text-blue-800 bg-transparent border-0 p-0 cursor-pointer font-inherit"
                >
                  {children}
                </button>
              );
            }
            // In-page anchor: smooth-scroll to the heading with matching id.
            // Mirrors DynamicTocSidebar's behavior so markdown TOC links and
            // sidebar clicks feel identical instead of opening a new tab.
            if (typeof href === "string" && href.startsWith("#") && href.length > 1) {
              const rawId = href.slice(1);
              return (
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const id = (() => {
                      try {
                        return decodeURIComponent(rawId);
                      } catch {
                        return rawId;
                      }
                    })();
                    const el = document.getElementById(id);
                    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
                  }}
                  className="text-blue-600 underline hover:text-blue-800 bg-transparent border-0 p-0 cursor-pointer font-inherit"
                >
                  {children}
                </button>
              );
            }
            return (
              <a href={href} target="_blank" rel="noopener noreferrer" {...rest}>
                {children}
              </a>
            );
          },
          h1: ({ node, children, ...props }) => <HeadingWithId level={1} node={node} {...props}>{children}</HeadingWithId>,
          h2: ({ node, children, ...props }) => <HeadingWithId level={2} node={node} {...props}>{children}</HeadingWithId>,
          h3: ({ node, children, ...props }) => <HeadingWithId level={3} node={node} {...props}>{children}</HeadingWithId>,
          input: ({ type, ...rest }) => {
            // Suppress native checkboxes from remark-gfm; handled by li override
            if (type === "checkbox") return null;
            return <input type={type} {...rest} />;
          },
          code: ({ children, className, ref: _ref, ...rest }) => {
            const match = /language-(\w+)/.exec(className || "");
            const isBlock =
              match != null ||
              (typeof children === "string" && children.includes("\n"));
            if (isBlock) {
              return (
                <SyntaxHighlighter
                  /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
                  style={oneDark as any}
                  language={match?.[1] ?? "python"}
                  PreTag="div"
                >
                  {String(children).replace(/\n$/, "")}
                </SyntaxHighlighter>
              );
            }
            return (
              <code className={className} {...rest}>
                {children}
              </code>
            );
          },
          blockquote: ({ children, className, node: _node, ...props }) => {
            const kind = getCalloutKindFromHast(_node as unknown as HastLike);
            if (!kind) {
              return <blockquote className={className} {...props}>{children}</blockquote>;
            }
            const merged = [calloutClass(kind), className].filter(Boolean).join(" ");
            return <blockquote className={merged} data-callout={kind} {...props}>{children}</blockquote>;
          },
          li: ({ children, className, node: _node, ...props }) => {
            if (!className?.includes("task-list-item")) {
              return <li {...props}>{children}</li>;
            }

            // Read checked state from hast node's input child. Typed via
            // @types/hast (Element/ElementContent) instead of `any` -- the
            // `type === "element"` narrowing is strictly safer than the old
            // untyped access and behavior-identical for real <input> nodes.
            const inputChild = (_node?.children as ElementContent[] | undefined)?.find(
              (c): c is Element =>
                c.type === "element" &&
                c.tagName === "input" &&
                c.properties?.type === "checkbox",
            );
            const isChecked = inputChild?.properties?.checked === true;

            // Line index from hast node position (1-based -> 0-based)
            const lineIdx = (_node?.position?.start?.line ?? 1) - 1;

            // Filter out null and input children
            const childArray = Array.isArray(children) ? children : [children];
            const textChildren = childArray.filter(
              (c) =>
                c !== null &&
                !(typeof c === "object" && c !== null && "type" in c && (c as React.ReactElement).type === "input"),
            );

            return (
              <li
                {...props}
                className={`list-none flex items-start gap-2 my-0.5 ${onCheckboxClick ? "cursor-pointer select-none" : ""}`}
                onClick={onCheckboxClick ? (e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onCheckboxClick(lineIdx);
                } : undefined}
              >
                {isChecked ? <CheckIcon /> : <UncheckedIcon />}
                {/* Checked items keep the leading check icon only -- no
                    strikethrough / muted text (per user UX preference,
                    Discord 2026-05-19). Applies app-wide to all task lists. */}
                <span>
                  {textChildren}
                </span>
              </li>
            );
          },
        }}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}
