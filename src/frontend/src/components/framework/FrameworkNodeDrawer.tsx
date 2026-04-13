import { useQuery } from "@tanstack/react-query";
import SlideOverPanel from "../ui/SlideOverPanel";
import MarkdownPreview from "../ui/MarkdownPreview";
import { api } from "../../utils/api";
import type { FrameworkNode } from "../../types/framework";

interface FrameworkNodeDrawerProps {
  nodeId: number | null;
  onClose: () => void;
}

export default function FrameworkNodeDrawer({ nodeId, onClose }: FrameworkNodeDrawerProps) {
  const open = nodeId !== null;
  const { data: node, isLoading } = useQuery<FrameworkNode>({
    queryKey: ["framework", "node", nodeId],
    queryFn: () => api.get<FrameworkNode>(`/framework/nodes/${nodeId}`),
    enabled: open,
    staleTime: 60_000,
  });

  const title = node?.title ?? (isLoading ? "Loading..." : "Node");
  const description = node?.description ?? null;

  return (
    <SlideOverPanel open={open} onClose={onClose} title={title}>
      {isLoading ? (
        <div className="text-gray-400 italic">Loading...</div>
      ) : description ? (
        <div className="prep-prose">
          <MarkdownPreview markdown={description} />
        </div>
      ) : (
        <div className="text-gray-400 italic">
          No notes yet for this topic.
        </div>
      )}
    </SlideOverPanel>
  );
}
