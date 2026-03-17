/**
 * Study Radio page -- queue management, now playing, and history.
 *
 * Sections:
 * 1. Quick Start: company filter + engine select + Start Radio button
 * 2. Now Playing: current item with progress
 * 3. Queue: ranked list with urgency, type badge, progress per item
 * 4. History: recently completed items
 */
import { useCallback, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useAudioPlayerContext } from "../contexts/AudioPlayerContext";
import { useToast } from "../contexts/ToastContext";
import { api } from "../utils/api";
import type { Company } from "../types/company";
import type { AudioPlayerItem, ContentType, ListeningStats, QueueItem, QueueResponse } from "../types/reading";
import Badge from "../components/ui/Badge";
import TranscriptViewer from "../components/reading/TranscriptViewer";

/** Map content_type to badge config. */
const CONTENT_BADGE: Record<ContentType, { label: string; variant: "blue" | "green" | "purple" }> = {
  framework_node: { label: "Framework", variant: "blue" },
  prep_notes: { label: "Prep Notes", variant: "green" },
  interview_question: { label: "Question", variant: "purple" },
};

/** Progress label based on queue item state. */
function progressLabel(item: QueueItem): { text: string; color: string } {
  if (item.completed) {
    return { text: "Done", color: "text-green-600" };
  }
  if (item.char_offset > 0 || item.last_chunk_index > 0) {
    const pct = item.total_chars > 0 ? Math.round((item.char_offset / item.total_chars) * 100) : 0;
    return { text: `${pct}%`, color: "text-yellow-600" };
  }
  return { text: "Not started", color: "text-gray-400" };
}

/** Format urgency as a human-friendly label. */
function urgencyLabel(urgency: number): string {
  if (urgency >= 80) return "High";
  if (urgency >= 50) return "Med";
  return "Low";
}

function urgencyColor(urgency: number): string {
  if (urgency >= 80) return "text-red-500";
  if (urgency >= 50) return "text-yellow-500";
  return "text-gray-400";
}

/** Format seconds as m:ss. */
function fmtTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export default function StudyRadio() {
  const {
    status,
    currentItem,
    queue: playerQueue,
    currentTime,
    duration,
    autoAdvance,
    error,
    play,
    togglePlayPause,
    skipNext,
    skipPrev,
    startRadio,
    setAutoAdvance,
  } = useAudioPlayerContext();
  const toast = useToast();
  const navigate = useNavigate();

  // Filters
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>("");
  const [engineSelect, setEngineSelect] = useState<string>("edge");
  const [readingItem, setReadingItem] = useState<QueueItem | null>(null);

  // Fetch companies for filter dropdown
  const companiesQuery = useQuery<Company[]>({
    queryKey: ["companies"],
    queryFn: () => api.get<Company[]>("/companies"),
  });

  // Fetch listening stats
  const statsQuery = useQuery<ListeningStats>({
    queryKey: ["reading-stats"],
    queryFn: () => api.get<ListeningStats>("/reading/stats"),
  });

  // Fetch reading queue
  const queueQuery = useQuery<QueueResponse>({
    queryKey: ["reading-queue", selectedCompanyId],
    queryFn: () =>
      api.get<QueueResponse>("/reading/queue", {
        params: {
          ...(selectedCompanyId ? { company_ids: selectedCompanyId } : {}),
          limit: 50,
        },
      }),
  });

  // Separate queue items into pending and completed
  const { pendingItems, completedItems } = useMemo(() => {
    const items = queueQuery.data?.items ?? [];
    const pending: QueueItem[] = [];
    const completed: QueueItem[] = [];
    for (const item of items) {
      if (item.completed) {
        completed.push(item);
      } else {
        pending.push(item);
      }
    }
    return { pendingItems: pending, completedItems: completed };
  }, [queueQuery.data]);

  // Check if an item is currently playing
  const isPlaying = useCallback(
    (item: QueueItem) =>
      currentItem?.content_type === item.content_type &&
      currentItem?.content_id === item.content_id,
    [currentItem],
  );

  // Start radio with filtered queue
  const handleStartRadio = useCallback(async () => {
    const items: AudioPlayerItem[] = pendingItems.map((qi) => ({
      content_type: qi.content_type,
      content_id: qi.content_id,
      title: qi.title,
    }));
    if (items.length === 0) {
      toast.info("No pending items in queue");
      return;
    }
    await startRadio(items);
    toast.success(`Radio started with ${items.length} items`);
  }, [pendingItems, startRadio, toast]);

  // Play a specific queue item
  const handlePlayItem = useCallback(
    async (item: QueueItem) => {
      await play({
        content_type: item.content_type,
        content_id: item.content_id,
        title: item.title,
      });
    },
    [play],
  );

  /** Navigate to full-screen page for framework/prep, or open modal for questions. */
  const handleReadItem = useCallback(
    (item: QueueItem) => {
      if (item.content_type === "framework_node") {
        navigate(`/framework/${item.content_id}/notes`);
      } else if (item.content_type === "prep_notes") {
        navigate(`/companies/${item.content_id}/prep`);
      } else {
        setReadingItem(item);
      }
    },
    [navigate],
  );

  const progress = duration > 0 ? currentTime / duration : 0;
  const nowPlayingBadge = currentItem ? CONTENT_BADGE[currentItem.content_type] : null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Study Radio</h1>

      {/* Quick Start Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Quick Start</h2>
        <div className="flex flex-wrap items-end gap-4">
          {/* Company filter */}
          <div className="flex flex-col gap-1">
            <label htmlFor="company-filter" className="text-sm text-gray-600">
              Company
            </label>
            <select
              id="company-filter"
              value={selectedCompanyId}
              onChange={(e) => setSelectedCompanyId(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 text-sm min-w-[160px]"
            >
              <option value="">All companies</option>
              {companiesQuery.data?.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* Engine select */}
          <div className="flex flex-col gap-1">
            <label htmlFor="engine-select" className="text-sm text-gray-600">
              TTS Engine
            </label>
            <select
              id="engine-select"
              value={engineSelect}
              onChange={(e) => setEngineSelect(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 text-sm min-w-[140px]"
            >
              <option value="edge">Edge TTS</option>
              <option value="openai">OpenAI</option>
              <option value="browser">Browser</option>
            </select>
          </div>

          {/* Start Radio button */}
          <button
            onClick={handleStartRadio}
            disabled={status === "loading" || pendingItems.length === 0}
            className="px-5 py-2 bg-green-600 text-white font-medium rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {status === "loading" ? "Preparing..." : "Start Radio"}
          </button>

          {/* Auto-advance toggle */}
          <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
            <input
              type="checkbox"
              checked={autoAdvance}
              onChange={(e) => setAutoAdvance(e.target.checked)}
              className="rounded"
            />
            Auto-advance
          </label>
        </div>

        {pendingItems.length > 0 && (
          <p className="mt-3 text-sm text-gray-500">
            {pendingItems.length} item{pendingItems.length !== 1 ? "s" : ""} in queue
          </p>
        )}
      </div>

      {/* Error / empty-queue banner */}
      {error && (
        error.startsWith("empty:") ? (
          <div className="px-4 py-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-700 text-sm">
            {error.slice("empty:".length)}. Add study content to get started.
          </div>
        ) : (
          <div className="px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )
      )}

      {/* Listening Stats */}
      {statsQuery.data && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <p className="text-2xl font-bold text-blue-600">{statsQuery.data.total_sessions}</p>
            <p className="text-xs text-gray-500 mt-1">Total Sessions</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <p className="text-2xl font-bold text-green-600">
              {Math.round(statsQuery.data.total_listening_seconds / 60)}
            </p>
            <p className="text-xs text-gray-500 mt-1">Total Minutes</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <p className="text-2xl font-bold text-purple-600">{statsQuery.data.total_items_listened}</p>
            <p className="text-xs text-gray-500 mt-1">Items Listened</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <p className="text-2xl font-bold text-amber-600">{statsQuery.data.streak_days}</p>
            <p className="text-xs text-gray-500 mt-1">Day Streak</p>
          </div>
        </div>
      )}

      {/* Now Playing Section */}
      {status === "loading" && !currentItem && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Now Playing</h2>
          <div className="flex items-center gap-3 text-gray-400">
            <svg className="w-6 h-6 animate-spin" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" fill="none" strokeDasharray="31.4 31.4" />
            </svg>
            <span className="text-sm">Preparing audio...</span>
          </div>
        </div>
      )}
      {currentItem && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Now Playing</h2>
          <div className="flex items-center gap-4">
            {/* Transport controls */}
            <div className="flex items-center gap-2">
              <button
                onClick={skipPrev}
                className="w-8 h-8 flex items-center justify-center text-gray-500 hover:text-gray-900 transition-colors"
                title="Previous"
              >
                <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current">
                  <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z" />
                </svg>
              </button>
              <button
                onClick={togglePlayPause}
                disabled={status === "loading"}
                className="w-12 h-12 flex items-center justify-center bg-green-600 text-white rounded-full hover:bg-green-700 disabled:opacity-50 transition-colors"
                title={status === "playing" ? "Pause" : "Play"}
              >
                {status === "loading" ? (
                  <svg className="w-6 h-6 animate-spin" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" fill="none" strokeDasharray="31.4 31.4" />
                  </svg>
                ) : status === "playing" ? (
                  <svg viewBox="0 0 24 24" className="w-6 h-6 fill-current">
                    <path d="M6 4h4v16H6zM14 4h4v16h-4z" />
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" className="w-6 h-6 fill-current">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                )}
              </button>
              <button
                onClick={skipNext}
                className="w-8 h-8 flex items-center justify-center text-gray-500 hover:text-gray-900 transition-colors"
                title="Next"
              >
                <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current">
                  <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z" />
                </svg>
              </button>
            </div>

            {/* Title + badge + progress */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                {nowPlayingBadge && (
                  <Badge variant={nowPlayingBadge.variant}>{nowPlayingBadge.label}</Badge>
                )}
                <span className="text-sm font-medium text-gray-900 truncate">
                  {currentItem.title}
                </span>
              </div>
              {/* Progress bar */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400 w-10 text-right shrink-0">
                  {fmtTime(currentTime)}
                </span>
                <div className="flex-1 h-1.5 bg-gray-200 rounded-full">
                  <div
                    className="h-full bg-green-500 rounded-full transition-[width] duration-100"
                    style={{ width: `${progress * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-400 w-10 shrink-0">
                  {fmtTime(duration)}
                </span>
              </div>
            </div>
          </div>

          {/* Queue position indicator */}
          {playerQueue.length > 0 && (
            <p className="mt-2 text-xs text-gray-400">
              {playerQueue.findIndex(
                (qi) =>
                  qi.content_type === currentItem.content_type &&
                  qi.content_id === currentItem.content_id,
              ) + 1}{" "}
              of {playerQueue.length} in queue
              {autoAdvance ? " (auto-advance on)" : ""}
            </p>
          )}
        </div>
      )}

      {/* Queue Section */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800">
            Queue{" "}
            <span className="text-sm font-normal text-gray-400">
              ({pendingItems.length} pending)
            </span>
          </h2>
          {queueQuery.isFetching && (
            <span className="text-xs text-gray-400">Refreshing...</span>
          )}
        </div>

        {queueQuery.isLoading ? (
          <div className="px-5 py-8 text-center text-gray-400 text-sm">
            Loading queue...
          </div>
        ) : pendingItems.length === 0 ? (
          <div className="px-5 py-8 text-center text-gray-400 text-sm">
            No pending items. All caught up!
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {pendingItems.map((item, idx) => {
              const badge = CONTENT_BADGE[item.content_type];
              const prog = progressLabel(item);
              const playing = isPlaying(item);

              return (
                <div
                  key={`${item.content_type}:${item.content_id}`}
                  className={`px-5 py-3 flex items-center gap-3 ${
                    playing ? "bg-green-50" : "hover:bg-gray-50"
                  } transition-colors`}
                >
                  {/* Index */}
                  <span className="text-sm text-gray-400 w-6 text-right shrink-0">
                    {playing ? (
                      <span className="text-green-600 font-bold">{"\u25B6"}</span>
                    ) : (
                      idx + 1
                    )}
                  </span>

                  {/* Title + badge */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <Badge variant={badge.variant}>{badge.label}</Badge>
                      <span className="text-sm text-gray-800 truncate">{item.title}</span>
                    </div>
                  </div>

                  {/* Urgency */}
                  <span
                    className={`text-xs font-medium shrink-0 ${urgencyColor(item.urgency)}`}
                    title={`Urgency: ${item.urgency}`}
                  >
                    {urgencyLabel(item.urgency)}
                  </span>

                  {/* Progress */}
                  <span className={`text-xs shrink-0 w-20 text-right ${prog.color}`}>
                    {prog.text}
                  </span>

                  {/* Read + Play buttons */}
                  <button
                    onClick={() => handleReadItem(item)}
                    className="px-2.5 py-1 text-xs border border-gray-300 text-gray-600 rounded hover:bg-gray-100 transition-colors shrink-0"
                    title="Read transcript"
                  >
                    Read
                  </button>
                  <button
                    onClick={() => handlePlayItem(item)}
                    disabled={playing && status === "loading"}
                    className="px-2.5 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 transition-colors shrink-0"
                    title="Play this item"
                  >
                    {playing && status === "playing" ? "Playing" : "Play"}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* History Section */}
      {completedItems.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-5 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-800">
              History{" "}
              <span className="text-sm font-normal text-gray-400">
                ({completedItems.length} completed)
              </span>
            </h2>
          </div>
          <div className="divide-y divide-gray-100">
            {completedItems.map((item) => {
              const badge = CONTENT_BADGE[item.content_type];
              return (
                <div
                  key={`${item.content_type}:${item.content_id}`}
                  className="px-5 py-3 flex items-center gap-3 hover:bg-gray-50 transition-colors"
                >
                  <span className="text-sm text-gray-300 w-6 text-right shrink-0">
                    {"\u2713"}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <Badge variant={badge.variant}>{badge.label}</Badge>
                      <span className="text-sm text-gray-500 truncate">{item.title}</span>
                    </div>
                  </div>
                  <span className="text-xs text-green-600 shrink-0">Done</span>
                  <button
                    onClick={() => handleReadItem(item)}
                    className="px-2.5 py-1 text-xs border border-gray-300 text-gray-600 rounded hover:bg-gray-100 transition-colors shrink-0"
                    title="Read transcript"
                  >
                    Read
                  </button>
                  <button
                    onClick={() => handlePlayItem(item)}
                    className="px-2.5 py-1 text-xs bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors shrink-0"
                    title="Replay this item"
                  >
                    Replay
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Transcript Viewer overlay */}
      {readingItem && (
        <TranscriptViewer
          contentType={readingItem.content_type}
          contentId={readingItem.content_id}
          title={readingItem.title}
          onClose={() => setReadingItem(null)}
          onListen={() => handlePlayItem(readingItem)}
        />
      )}
    </div>
  );
}
