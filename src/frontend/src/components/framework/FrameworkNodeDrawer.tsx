import { useQuery } from "@tanstack/react-query";
import SlideOverPanel from "../ui/SlideOverPanel";
import MarkdownPreview from "../ui/MarkdownPreview";
import GoldenToggleButton from "../ui/GoldenToggleButton";
import { api } from "../../utils/api";
import type { FrameworkNode } from "../../types/framework";

interface FrameworkNodeDrawerProps {
  nodeId: number | null;
  onClose: () => void;
  /**
   * Called when the node's markdown body contains a `kg://N` link. Wired by
   * the KnowledgeGraph page to swap the active node id in-place (re-uses the
   * same drawer instance, no full-page navigation).
   */
  onKgLinkClick?: (kgId: number) => void;
}

export default function FrameworkNodeDrawer({ nodeId, onClose, onKgLinkClick }: FrameworkNodeDrawerProps) {
  const open = nodeId !== null;
  const { data: node, isLoading } = useQuery<FrameworkNode>({
    queryKey: ["framework", "node", nodeId],
    queryFn: () => api.get<FrameworkNode>(`/framework/nodes/${nodeId}`),
    enabled: open,
    staleTime: 60_000,
  });

  const title = node?.title ?? (isLoading ? "Loading..." : "Node");
  const description = node?.description ?? null;
  const isGolden = node?.is_golden ?? false;

  const headerActions = node ? (
    <GoldenToggleButton
      itemType="framework_node"
      itemId={node.id}
      isGolden={isGolden}
    />
  ) : null;

  return (
    <SlideOverPanel
      open={open}
      onClose={onClose}
      title={title}
      headerActions={headerActions}
      headerAccentClassName={isGolden ? "border-t-2 border-t-orange-300" : ""}
    >
      {isLoading ? (
        <div className="text-gray-400 italic">Loading...</div>
      ) : description ? (
        <div className="prep-prose">
          <MarkdownPreview markdown={description} onKgLinkClick={onKgLinkClick} />
        </div>
      ) : (
        <div className="text-gray-400 italic">
          No notes yet for this topic.
        </div>
      )}
    </SlideOverPanel>
  );
}
