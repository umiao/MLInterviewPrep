/**
 * Persistent bottom bar for audio playback (Spotify-style).
 * Shows current item, transport controls, progress, speed, and queue.
 * Only visible when the player is active (not idle).
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { useAudioPlayerContext } from "../contexts/AudioPlayerContext";
import { SPEED_OPTIONS } from "../hooks/useAudioPlayer";
import type { PlaybackSpeed } from "../hooks/useAudioPlayer";
import type { ContentType } from "../types/reading";
import Badge from "./ui/Badge";

/** Map content_type to a human-readable badge label and color. */
const CONTENT_BADGE: Record<ContentType, { label: string; variant: "blue" | "green" | "purple" }> = {
  framework_node: { label: "Framework", variant: "blue" },
  prep_notes: { label: "Prep Notes", variant: "green" },
  interview_question: { label: "Question", variant: "purple" },
};

/** Format seconds as m:ss. */
function fmtTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export default function AudioPlayerBar() {
  const {
    status,
    currentItem,
    queue,
    currentTime,
    duration,
    speed,
    autoAdvance,
    error,
    togglePlayPause,
    skipNext,
    skipPrev,
    setSpeed,
    seek,
    stop,
  } = useAudioPlayerContext();

  const [showQueue, setShowQueue] = useState(false);
  const [showSpeedMenu, setShowSpeedMenu] = useState(false);
  const speedMenuRef = useRef<HTMLDivElement>(null);
  const queuePanelRef = useRef<HTMLDivElement>(null);

  // Close menus on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (showSpeedMenu && speedMenuRef.current && !speedMenuRef.current.contains(e.target as Node)) {
        setShowSpeedMenu(false);
      }
      if (showQueue && queuePanelRef.current && !queuePanelRef.current.contains(e.target as Node)) {
        setShowQueue(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [showSpeedMenu, showQueue]);

  // Keyboard shortcuts: Space = play/pause, N = next (only when not in input)
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const tag = (e.target as HTMLElement).tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
      if ((e.target as HTMLElement).isContentEditable) return;

      if (e.code === "Space") {
        e.preventDefault();
        togglePlayPause();
      } else if (e.key === "n" || e.key === "N") {
        skipNext();
      }
    }
    // Only bind when player is active
    if (status === "playing" || status === "paused") {
      document.addEventListener("keydown", handleKeyDown);
      return () => document.removeEventListener("keydown", handleKeyDown);
    }
  }, [status, togglePlayPause, skipNext]);

  // Don't render when idle and no error
  if (status === "idle" && !error) return null;

  const progress = duration > 0 ? currentTime / duration : 0;
  const badge = currentItem ? CONTENT_BADGE[currentItem.content_type] : null;

  const handleProgressClick = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      const rect = e.currentTarget.getBoundingClientRect();
      const fraction = (e.clientX - rect.left) / rect.width;
      seek(fraction);
    },
    [seek],
  );

  const handleSpeedSelect = useCallback(
    (s: PlaybackSpeed) => {
      setSpeed(s);
      setShowSpeedMenu(false);
    },
    [setSpeed],
  );

  const handleClose = useCallback(() => {
    stop();
    setShowQueue(false);
    setShowSpeedMenu(false);
  }, [stop]);

  return (
    <>
      {/* Queue slide-out panel */}
      {showQueue && (
        <div
          ref={queuePanelRef}
          className="fixed bottom-16 right-4 w-80 max-h-80 bg-gray-900 text-gray-200 rounded-t-lg shadow-2xl border border-gray-700 overflow-hidden z-50"
        >
          <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
            <span className="text-sm font-semibold text-white">
              Queue {autoAdvance ? "(Radio)" : ""}
            </span>
            <button
              onClick={() => setShowQueue(false)}
              className="text-gray-400 hover:text-white text-sm"
            >
              Close
            </button>
          </div>
          <div className="overflow-y-auto max-h-64">
            {queue.length === 0 ? (
              <div className="px-4 py-6 text-center text-gray-500 text-sm">
                No items in queue
              </div>
            ) : (
              queue.map((item, idx) => {
                const isPlaying =
                  currentItem?.content_type === item.content_type &&
                  currentItem?.content_id === item.content_id;
                const itemBadge = CONTENT_BADGE[item.content_type];
                return (
                  <div
                    key={`${item.content_type}:${item.content_id}`}
                    className={`px-4 py-2 flex items-center gap-2 text-sm ${
                      isPlaying ? "bg-gray-700" : "hover:bg-gray-800"
                    }`}
                  >
                    <span className="text-gray-500 w-5 text-right shrink-0">
                      {isPlaying ? "\u25B6" : idx + 1}
                    </span>
                    <span className="truncate flex-1">{item.title}</span>
                    <Badge variant={itemBadge.variant}>{itemBadge.label}</Badge>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}

      {/* Main player bar */}
      <div className="fixed bottom-0 left-0 right-0 h-16 bg-gray-900 text-white flex items-center px-4 gap-3 shadow-lg z-50 border-t border-gray-700">
        {/* Title + badge */}
        <div className="flex items-center gap-2 w-48 shrink-0 min-w-0">
          {currentItem ? (
            <>
              {badge && <Badge variant={badge.variant}>{badge.label}</Badge>}
              <span className="text-sm truncate" title={currentItem.title}>
                {currentItem.title}
              </span>
            </>
          ) : error ? (
            <span className="text-sm text-red-400 truncate">{error}</span>
          ) : null}
        </div>

        {/* Transport controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={skipPrev}
            className="w-8 h-8 flex items-center justify-center text-gray-300 hover:text-white transition-colors"
            title="Previous"
          >
            <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
              <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z" />
            </svg>
          </button>
          <button
            onClick={togglePlayPause}
            disabled={status === "loading"}
            className="w-10 h-10 flex items-center justify-center bg-white text-gray-900 rounded-full hover:bg-gray-200 disabled:opacity-50 transition-colors"
            title={status === "playing" ? "Pause (Space)" : "Play (Space)"}
          >
            {status === "loading" ? (
              <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" fill="none" strokeDasharray="31.4 31.4" />
              </svg>
            ) : status === "playing" ? (
              <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current">
                <path d="M6 4h4v16H6zM14 4h4v16h-4z" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current">
                <path d="M8 5v14l11-7z" />
              </svg>
            )}
          </button>
          <button
            onClick={skipNext}
            className="w-8 h-8 flex items-center justify-center text-gray-300 hover:text-white transition-colors"
            title="Next (N)"
          >
            <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
              <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z" />
            </svg>
          </button>
        </div>

        {/* Progress bar + times */}
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className="text-xs text-gray-400 w-10 text-right shrink-0">
            {fmtTime(currentTime)}
          </span>
          <div
            className="flex-1 h-1.5 bg-gray-700 rounded-full cursor-pointer group relative"
            onClick={handleProgressClick}
            title="Seek"
          >
            <div
              className="h-full bg-green-500 rounded-full transition-[width] duration-100"
              style={{ width: `${progress * 100}%` }}
            />
            <div
              className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
              style={{ left: `calc(${progress * 100}% - 6px)` }}
            />
          </div>
          <span className="text-xs text-gray-400 w-10 shrink-0">
            {fmtTime(duration)}
          </span>
        </div>

        {/* Speed selector */}
        <div className="relative" ref={speedMenuRef}>
          <button
            onClick={() => setShowSpeedMenu(!showSpeedMenu)}
            className="px-2 py-1 text-xs font-medium text-gray-300 hover:text-white border border-gray-600 rounded transition-colors"
            title="Playback speed"
          >
            {speed}x
          </button>
          {showSpeedMenu && (
            <div className="absolute bottom-full mb-2 right-0 bg-gray-800 border border-gray-600 rounded shadow-lg py-1 min-w-[80px]">
              {SPEED_OPTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => handleSpeedSelect(s)}
                  className={`block w-full text-left px-3 py-1.5 text-xs hover:bg-gray-700 transition-colors ${
                    s === speed ? "text-green-400 font-medium" : "text-gray-300"
                  }`}
                >
                  {s}x
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Queue toggle */}
        <button
          onClick={() => setShowQueue(!showQueue)}
          className={`px-2 py-1 text-xs font-medium border rounded transition-colors ${
            showQueue
              ? "text-green-400 border-green-500"
              : "text-gray-300 hover:text-white border-gray-600"
          }`}
          title="Queue"
        >
          <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current inline-block">
            <path d="M4 6h16v2H4zm0 5h16v2H4zm0 5h12v2H4zm14 0h2v4h-2zm2-2h2v2h-2z" />
          </svg>
          {queue.length > 0 && (
            <span className="ml-1">{queue.length}</span>
          )}
        </button>

        {/* Close button */}
        <button
          onClick={handleClose}
          className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white transition-colors"
          title="Close player"
        >
          <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
          </svg>
        </button>
      </div>
    </>
  );
}
