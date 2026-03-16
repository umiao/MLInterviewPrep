import type { FrameworkNode } from "../../types/framework";

interface BreadcrumbPathProps {
  node: FrameworkNode;
  nodeMap: Map<number, FrameworkNode>;
  onNavigate: (node: FrameworkNode) => void;
}

/** Build ancestor chain from root to the given node. */
function getAncestorChain(
  node: FrameworkNode,
  nodeMap: Map<number, FrameworkNode>,
): FrameworkNode[] {
  const chain: FrameworkNode[] = [node];
  let current = node;
  while (current.parent_id !== null) {
    const parent = nodeMap.get(current.parent_id);
    if (!parent) break;
    chain.unshift(parent);
    current = parent;
  }
  return chain;
}

export default function BreadcrumbPath({
  node,
  nodeMap,
  onNavigate,
}: BreadcrumbPathProps) {
  const chain = getAncestorChain(node, nodeMap);

  return (
    <nav className="flex items-center gap-1 text-sm text-gray-500 flex-wrap">
      {chain.map((segment, i) => {
        const isLast = i === chain.length - 1;
        return (
          <span key={segment.id} className="flex items-center gap-1">
            {i > 0 && (
              <svg
                className="w-3 h-3 text-gray-300 shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            )}
            {isLast ? (
              <span className="font-medium text-gray-700">{segment.title}</span>
            ) : (
              <button
                className="hover:text-blue-600 hover:underline transition-colors"
                onClick={() => onNavigate(segment)}
              >
                {segment.title}
              </button>
            )}
          </span>
        );
      })}
    </nav>
  );
}
