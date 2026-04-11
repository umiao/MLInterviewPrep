import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeRaw from "rehype-raw";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import "katex/dist/katex.min.css";
import { slugify, type TocHeading } from "../../utils/slugify";

interface MarkdownPreviewProps {
  markdown: string;
  onCheckboxClick?: (lineIndex: number) => void;
  onHeadingsExtracted?: (headings: TocHeading[]) => void;
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
}: MarkdownPreviewProps) {
  const headingsRef = useRef<TocHeading[]>([]);
  const prevJsonRef = useRef<string>("");

  // After each render, emit collected headings if changed
  useEffect(() => {
    if (!onHeadingsExtracted) return;
    const json = JSON.stringify(headingsRef.current);
    if (json !== prevJsonRef.current) {
      prevJsonRef.current = json;
      onHeadingsExtracted(headingsRef.current);
    }
  });

  // Reset headings collector before each render
  headingsRef.current = [];

  /** Factory for heading components that record heading info and add IDs. */
  function HeadingWithId({ level, children, ...props }: { level: number; children?: React.ReactNode } & React.HTMLAttributes<HTMLHeadingElement>) {
    const text = childrenToText(children);
    const id = slugify(text);
    headingsRef.current.push({ level, text, id });
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
        components={{
          h1: ({ children, ...props }) => <HeadingWithId level={1} {...props}>{children}</HeadingWithId>,
          h2: ({ children, ...props }) => <HeadingWithId level={2} {...props}>{children}</HeadingWithId>,
          h3: ({ children, ...props }) => <HeadingWithId level={3} {...props}>{children}</HeadingWithId>,
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
          li: ({ children, className, node: _node, ...props }) => {
            if (!className?.includes("task-list-item")) {
              return <li {...props}>{children}</li>;
            }

            // Read checked state from hast node's input child
            const inputChild = (_node?.children as any[])?.find(
              (c: any) => c.tagName === "input" && c.properties?.type === "checkbox"
            );
            const isChecked = !!inputChild?.properties?.checked;

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
                <span className={isChecked ? "line-through text-gray-400" : ""}>
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
