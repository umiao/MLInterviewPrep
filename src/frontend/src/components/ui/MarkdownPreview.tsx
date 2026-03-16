import ReactMarkdown from "react-markdown";

interface MarkdownPreviewProps {
  markdown: string;
  onCheckboxClick: (lineIndex: number) => void;
}

/**
 * Renders markdown with clickable checkboxes.
 * Shared by PrepNotesTab (inline panel) and PrepNotesPage (full screen).
 */
export default function MarkdownPreview({
  markdown,
  onCheckboxClick,
}: MarkdownPreviewProps) {
  // Build a map: which list items correspond to checkbox lines
  const lines = markdown.split("\n");
  const checkboxLineIndices: number[] = [];
  for (let i = 0; i < lines.length; i++) {
    const trimmed = lines[i].trimStart();
    if (/^[-*]\s*\[[ xX]\]/.test(trimmed)) {
      checkboxLineIndices.push(i);
    }
  }

  // Track which checkbox item we're rendering
  let checkboxCounter = 0;

  return (
    <ReactMarkdown
      components={{
        li: ({ children, ...props }) => {
          // Detect if this li contains a checkbox (input type=checkbox)
          const childArray = Array.isArray(children) ? children : [children];
          const hasCheckbox = childArray.some(
            (child) =>
              typeof child === "object" &&
              child !== null &&
              "type" in child &&
              (child as React.ReactElement).type === "input",
          );

          if (hasCheckbox && checkboxCounter < checkboxLineIndices.length) {
            const lineIdx = checkboxLineIndices[checkboxCounter];
            checkboxCounter++;
            const isChecked = /^[-*]\s*\[[xX]\]/.test(
              lines[lineIdx].trimStart(),
            );

            return (
              <li
                {...props}
                className="list-none flex items-start gap-1.5 cursor-pointer select-none"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onCheckboxClick(lineIdx);
                }}
              >
                <span className="mt-0.5 shrink-0">
                  {isChecked ? (
                    <span className="inline-block w-4 h-4 border-2 border-blue-500 bg-blue-500 rounded text-white text-xs leading-4 text-center">
                      x
                    </span>
                  ) : (
                    <span className="inline-block w-4 h-4 border-2 border-gray-300 rounded" />
                  )}
                </span>
                <span className={isChecked ? "line-through text-gray-400" : ""}>
                  {childArray.filter(
                    (child) =>
                      !(
                        typeof child === "object" &&
                        child !== null &&
                        "type" in child &&
                        (child as React.ReactElement).type === "input"
                      ),
                  )}
                </span>
              </li>
            );
          }

          return <li {...props}>{children}</li>;
        },
      }}
    >
      {markdown}
    </ReactMarkdown>
  );
}
