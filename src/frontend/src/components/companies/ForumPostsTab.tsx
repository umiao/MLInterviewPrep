import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../utils/api";
import MarkdownPreview from "../ui/MarkdownPreview";
import {
  useForumSeeds,
  useForumLinks,
  useForumProgress,
  useScrapeLinks,
  useFetchNext,
  useFetchPost,
  useImportPost,
  type ForumSeed,
  type ForumPostLink,
  type ForumPost,
} from "../../hooks/useForumPosts";

interface ForumPostsTabProps {
  companyId: number;
}

/**
 * Tab content showing forum seeds and post links for a company.
 * Supports Phase A (scrape links) and Phase B (fetch posts) workflows.
 */
export default function ForumPostsTab({ companyId }: ForumPostsTabProps) {
  const { data: seeds, isLoading: seedsLoading } = useForumSeeds(companyId);
  const [selectedSeedId, setSelectedSeedId] = useState<number | null>(null);

  if (seedsLoading) {
    return <p className="text-gray-400 text-sm">Loading forum seeds...</p>;
  }

  if (!seeds?.length) {
    return (
      <p className="text-gray-400 italic text-sm">
        No forum seeds for this company. Add seeds via the CLI or API.
      </p>
    );
  }

  const activeSeed = seeds.find((s) => s.id === selectedSeedId) ?? seeds[0];

  return (
    <div className="flex flex-col gap-4">
      {/* Seed selector */}
      {seeds.length > 1 && (
        <SeedSelector
          seeds={seeds}
          selectedId={activeSeed.id}
          onSelect={setSelectedSeedId}
        />
      )}
      <SeedDetail seed={activeSeed} companyId={companyId} />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Sub-components                                                    */
/* ------------------------------------------------------------------ */

function SeedSelector({
  seeds,
  selectedId,
  onSelect,
}: {
  seeds: ForumSeed[];
  selectedId: number;
  onSelect: (id: number) => void;
}) {
  return (
    <div className="flex gap-2 flex-wrap">
      {seeds.map((s) => (
        <button
          key={s.id}
          onClick={() => onSelect(s.id)}
          className={`text-xs px-3 py-1.5 rounded border ${
            s.id === selectedId
              ? "bg-blue-100 border-blue-300 text-blue-700 font-medium"
              : "border-gray-200 text-gray-600 hover:bg-gray-50"
          }`}
        >
          {s.label || s.url}
        </button>
      ))}
    </div>
  );
}

function SeedDetail({
  seed,
  companyId,
}: {
  seed: ForumSeed;
  companyId: number;
}) {
  const { data: links, isLoading: linksLoading } = useForumLinks(seed.id);
  const { data: progress } = useForumProgress(seed.id);
  const scrape = useScrapeLinks(seed.id);
  const fetchNext = useFetchNext(seed.id);

  return (
    <div className="flex flex-col gap-3">
      {/* Progress bar + actions */}
      <div className="flex items-center gap-3 flex-wrap">
        {progress && progress.total > 0 && (
          <ProgressBar fetched={progress.fetched} total={progress.total} />
        )}
        <div className="flex gap-2">
          <ActionButton
            label="Scrape Links"
            onClick={() => scrape.mutate()}
            isPending={scrape.isPending}
          />
          <ActionButton
            label="Fetch Next"
            onClick={() => fetchNext.mutate()}
            isPending={fetchNext.isPending}
            disabled={!progress || progress.pending === 0}
          />
        </div>
        {scrape.isError && (
          <span className="text-xs text-red-500">
            Scrape failed: {scrape.error.message}
          </span>
        )}
        {fetchNext.isError && (
          <span className="text-xs text-red-500">
            Fetch failed: {fetchNext.error.message}
          </span>
        )}
      </div>

      {/* Link list */}
      {linksLoading ? (
        <p className="text-gray-400 text-sm">Loading links...</p>
      ) : !links?.length ? (
        <p className="text-gray-400 text-sm italic">
          No links yet. Click &quot;Scrape Links&quot; to discover posts.
        </p>
      ) : (
        <div className="flex flex-col gap-1">
          {links.map((link) => (
            <LinkRow
              key={link.id}
              link={link}
              seedId={seed.id}
              companyId={companyId}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ProgressBar({ fetched, total }: { fetched: number; total: number }) {
  const pct = total > 0 ? Math.round((fetched / total) * 100) : 0;
  return (
    <div className="flex items-center gap-2 text-xs text-gray-600">
      <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-500 rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span>
        {fetched}/{total} fetched
      </span>
    </div>
  );
}

function ActionButton({
  label,
  onClick,
  isPending,
  disabled,
}: {
  label: string;
  onClick: () => void;
  isPending: boolean;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={isPending || disabled}
      className="text-xs px-3 py-1.5 rounded bg-blue-50 text-blue-700 hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {isPending ? `${label}...` : label}
    </button>
  );
}

function LinkRow({
  link,
  seedId,
  companyId,
}: {
  link: ForumPostLink;
  seedId: number;
  companyId: number;
}) {
  const [expanded, setExpanded] = useState(false);
  const fetchPost = useFetchPost();
  const importPost = useImportPost();
  const [imported, setImported] = useState(false);

  const statusColor: Record<string, string> = {
    pending: "bg-gray-200 text-gray-600",
    fetched: "bg-green-100 text-green-700",
    failed: "bg-red-100 text-red-600",
  };

  return (
    <div className="border border-gray-100 rounded">
      <div className="flex items-center gap-2 px-3 py-2 text-sm">
        {/* Status badge */}
        <span
          className={`text-xs px-2 py-0.5 rounded-full ${statusColor[link.status] ?? "bg-gray-100 text-gray-500"}`}
        >
          {link.status}
        </span>

        {/* Title / URL */}
        <button
          onClick={() => link.status === "fetched" && setExpanded(!expanded)}
          className={`flex-1 text-left truncate ${
            link.status === "fetched"
              ? "text-blue-700 hover:underline cursor-pointer"
              : "text-gray-700"
          }`}
          disabled={link.status !== "fetched"}
        >
          {link.title || link.url}
        </button>

        {/* Actions */}
        {link.status === "pending" && (
          <button
            onClick={() => fetchPost.mutate({ linkId: link.id, seedId })}
            disabled={fetchPost.isPending}
            className="text-xs px-2 py-1 rounded bg-blue-50 text-blue-700 hover:bg-blue-100 disabled:opacity-50"
          >
            {fetchPost.isPending ? "Fetching..." : "Fetch"}
          </button>
        )}
        {link.status === "fetched" && link.post_id != null && (
          <button
            onClick={() => {
              importPost.mutate(
                { postId: link.post_id!, companyId },
                { onSuccess: () => setImported(true) },
              );
            }}
            disabled={importPost.isPending || imported}
            className="text-xs px-2 py-1 rounded bg-green-50 text-green-700 hover:bg-green-100 disabled:opacity-50"
          >
            {imported ? "Imported" : importPost.isPending ? "Importing..." : "Import"}
          </button>
        )}
        {link.status === "failed" && link.last_error && (
          <span className="text-xs text-red-400 truncate max-w-[200px]" title={link.last_error}>
            {link.last_error}
          </span>
        )}
      </div>

      {/* Expanded raw text preview */}
      {expanded && link.status === "fetched" && link.post_id != null && (
        <ExpandedPost postId={link.post_id} />
      )}
    </div>
  );
}

function ExpandedPost({ postId }: { postId: number }) {
  const { data: post, isLoading } = useQuery<ForumPost>({
    queryKey: ["forumPost", postId],
    queryFn: () => api.get<ForumPost>(`/forum/posts/${postId}`),
    enabled: postId > 0,
  });

  if (isLoading) {
    return <div className="px-3 py-2 text-xs text-gray-400">Loading post...</div>;
  }
  if (!post) {
    return <div className="px-3 py-2 text-xs text-gray-400">Post not available.</div>;
  }

  return (
    <div className="border-t border-gray-100 px-3 py-2 max-h-64 overflow-auto bg-gray-50">
      <MarkdownPreview markdown={post.raw_text} />
    </div>
  );
}
