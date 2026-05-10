import { useMemo, useCallback } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import { useFrameworkNotes } from "../hooks/useFrameworkNotes";
import MarkdownPreview from "../components/ui/MarkdownPreview";
import PrevNextNav from "../components/ui/PrevNextNav";
import type { FrameworkNode, NodeStatus } from "../types/framework";

const STATUS_COLORS: Record<NodeStatus, string> = {
  not_started: "bg-red-400",
  in_progress: "bg-yellow-400",
  review: "bg-blue-400",
  mastered: "bg-green-400",
};

const STATUS_LABELS: Record<NodeStatus, string> = {
  not_started: "Not Started",
  in_progress: "In Progress",
  review: "Review",
  mastered: "Mastered",
};

/** Recursively collect all leaf nodes (no children). */
function collectLeaves(node: FrameworkNode): FrameworkNode[] {
  if (!node.children?.length) return [node];
  return node.children.flatMap(collectLeaves);
}

/** Group leaf descendants by their immediate parent category. */
function getGroupedLeaves(
  node: FrameworkNode,
): { category: string; leaves: FrameworkNode[] }[] {
  if (!node.children?.length) return [];

  const groups: { category: string; leaves: FrameworkNode[] }[] = [];
  for (const child of node.children) {
    if (!child.children?.length) continue; // skip direct leaves for now
    const leaves = collectLeaves(child);
    if (leaves.length > 0) {
      groups.push({ category: child.title, leaves });
    }
  }

  // If all direct children are leaves (no sub-categories), group under "Topics"
  if (groups.length === 0) {
    const directLeaves = node.children.filter((c) => !c.children?.length);
    if (directLeaves.length) {
      groups.push({ category: "Topics", leaves: directLeaves });
    }
  }

  return groups;
}

/** Flatten a tree into a list for sibling navigation. */
function flattenTree(nodes: FrameworkNode[]): FrameworkNode[] {
  const result: FrameworkNode[] = [];
  function walk(list: FrameworkNode[]) {
    for (const n of list) {
      result.push(n);
      if (n.children?.length) walk(n.children);
    }
  }
  walk(nodes);
  return result;
}

/** Build breadcrumb path from tree by finding the node and its ancestors. */
function buildBreadcrumbs(
  nodes: FrameworkNode[],
  targetId: number,
): FrameworkNode[] {
  const path: FrameworkNode[] = [];
  function find(list: FrameworkNode[], ancestors: FrameworkNode[]): boolean {
    for (const n of list) {
      if (n.id === targetId) {
        path.push(...ancestors, n);
        return true;
      }
      if (n.children?.length && find(n.children, [...ancestors, n])) {
        return true;
      }
    }
    return false;
  }
  find(nodes, []);
  return path;
}

/** Find siblings at the same depth sharing the same parent. */
function findSiblings(
  flat: FrameworkNode[],
  nodeId: number,
  parentId: number | null,
): { prev: FrameworkNode | null; next: FrameworkNode | null } {
  const siblings = flat.filter((n) => n.parent_id === parentId);
  const idx = siblings.findIndex((n) => n.id === nodeId);
  return {
    prev: idx > 0 ? siblings[idx - 1] : null,
    next: idx < siblings.length - 1 ? siblings[idx + 1] : null,
  };
}

/**
 * Full-screen framework notes page at /framework/:nodeId/notes.
 */
export default function FrameworkNotesPage() {
  const { nodeId: rawId } = useParams<{ nodeId: string }>();
  const nodeId = Number(rawId);
  const navigate = useNavigate();

  // Fetch the single node
  const { data: node, isLoading } = useQuery<FrameworkNode>({
    queryKey: ["framework", "node", nodeId],
    queryFn: () => api.get<FrameworkNode>(`/framework/nodes/${nodeId}`),
    enabled: nodeId > 0,
  });

  // Use cached tree for breadcrumbs and sibling nav
  const { data: tree } = useQuery<FrameworkNode[]>({
    queryKey: ["framework", "tree"],
    queryFn: () => api.get<FrameworkNode[]>("/framework/tree"),
    staleTime: 60_000,
  });

  const flat = useMemo(() => (tree ? flattenTree(tree) : []), [tree]);
  const breadcrumbs = useMemo(
    () => (tree ? buildBreadcrumbs(tree, nodeId) : []),
    [tree, nodeId],
  );

  // Find the current node in the tree (with children populated)
  const treeNode = useMemo(
    () => flat.find((n) => n.id === nodeId) ?? null,
    [flat, nodeId],
  );

  // Use tree-derived parent_id to avoid race with async node query
  const { prev, next } = useMemo(
    () => findSiblings(flat, nodeId, treeNode?.parent_id ?? null),
    [flat, nodeId, treeNode?.parent_id],
  );
  const groupedLeaves = useMemo(
    () => (treeNode ? getGroupedLeaves(treeNode) : []),
    [treeNode],
  );

  const handleFrameworkNav = useCallback(
    (id: number | string) => navigate(`/framework/${id}/notes`),
    [navigate],
  );

  const {
    notes,
    setNotes,
    mode,
    setMode,
    saveStatus,
    setSaveStatus,
    handleRetry,
    handleCheckboxClick,
  } = useFrameworkNotes({
    nodeId,
    initialNotes: node?.description ?? null,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        Loading...
      </div>
    );
  }

  if (!node) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <p className="text-gray-500">Node not found.</p>
        <Link to="/framework" className="text-blue-600 hover:text-blue-800 text-sm">
          Back to Framework
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Sticky header */}
      <header className="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-3 shrink-0">
        <div className="flex items-center justify-between">
          {/* Breadcrumbs */}
          <nav className="flex items-center gap-1 text-sm text-gray-500 min-w-0">
            <Link to="/framework" className="hover:text-gray-700 shrink-0">
              Framework
            </Link>
            {breadcrumbs.map((crumb, i) => (
              <span key={crumb.id} className="flex items-center gap-1 min-w-0">
                <span className="text-gray-300">/</span>
                {i < breadcrumbs.length - 1 ? (
                  <Link
                    to={`/framework/${crumb.id}/notes`}
                    className="hover:text-gray-700 truncate max-w-[120px]"
                    title={crumb.title}
                  >
                    {crumb.title}
                  </Link>
                ) : (
                  <span className="text-gray-800 font-medium truncate max-w-[200px]" title={crumb.title}>
                    {crumb.title}
                  </span>
                )}
              </span>
            ))}
          </nav>

          <div className="flex items-center gap-3 shrink-0">
            {/* Sibling navigation */}
            <PrevNextNav
              prev={prev ? { id: prev.id, label: prev.title } : null}
              next={next ? { id: next.id, label: next.title } : null}
              onNavigate={handleFrameworkNav}
              enableKeyboard={mode === "preview"}
            />

            {/* Mode toggle */}
            <div className="flex gap-1">
              <button
                onClick={() => setMode("preview")}
                className={`text-sm px-3 py-1.5 rounded ${
                  mode === "preview"
                    ? "bg-blue-100 text-blue-700 font-medium"
                    : "text-gray-500 hover:bg-gray-100"
                }`}
              >
                Preview
              </button>
              <button
                onClick={() => setMode("edit")}
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
          </div>
        </div>
      </header>

      {/* Content area */}
      <div className="flex-1 overflow-auto p-6 flex flex-col min-h-0">
        {mode === "edit" ? (
          <textarea
            value={notes}
            onChange={(e) => {
              setNotes(e.target.value);
              if (saveStatus === "saved" || saveStatus === "error") {
                setSaveStatus("idle");
              }
            }}
            className="flex-1 min-h-0 w-full border border-gray-300 rounded px-4 py-3 text-base font-mono resize-none"
            placeholder="Write markdown notes here...&#10;&#10;Use LaTeX: $E = mc^2$&#10;&#10;- [ ] Review this topic"
          />
        ) : (
          <div className="prep-prose">
            {notes ? (
              <MarkdownPreview
                markdown={notes}
                onCheckboxClick={handleCheckboxClick}
                onKgLinkClick={(id) => navigate(`/kg?node=n${id}`)}
              />
            ) : groupedLeaves.length > 0 ? (
              <div className="max-w-4xl">
                <h2 className="text-xl font-semibold text-gray-800 mb-6">
                  {node.title}
                </h2>
                {groupedLeaves.map((group) => (
                  <section key={group.category} className="mb-8">
                    <h3 className="text-lg font-bold text-gray-700 mb-3">
                      {group.category}
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                      {group.leaves.map((leaf) => (
                        <button
                          key={leaf.id}
                          onClick={() => handleFrameworkNav(leaf.id)}
                          className="text-left p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-sm transition-all"
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <span
                              className={`w-2.5 h-2.5 rounded-full shrink-0 ${STATUS_COLORS[leaf.status]}`}
                              title={STATUS_LABELS[leaf.status]}
                            />
                            <span className="text-sm font-medium text-gray-800 truncate">
                              {leaf.title}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-blue-500 rounded-full transition-all"
                                style={{ width: `${leaf.progress_pct}%` }}
                              />
                            </div>
                            <span className="text-xs text-gray-400 shrink-0">
                              {leaf.progress_pct}%
                            </span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </section>
                ))}
                <p className="text-sm text-gray-400 italic mt-4">
                  Switch to Edit mode to add overview notes for this topic.
                </p>
              </div>
            ) : (
              <p className="text-gray-400 italic">
                No notes yet. Switch to Edit mode to add some.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
