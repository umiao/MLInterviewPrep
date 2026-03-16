import { useCallback } from "react";
import { useAudioPlayerContext } from "../../contexts/AudioPlayerContext";
import type { ContentType } from "../../types/reading";

interface ListenButtonProps {
  contentType: ContentType;
  contentId: number;
  title?: string;
}

/**
 * Button that plays TTS audio for a content item via the global AudioPlayerContext.
 * Replaces the old self-contained audio approach with the shared player.
 */
export default function ListenButton({ contentType, contentId, title }: ListenButtonProps) {
  const { status, currentItem, play, pause, resume } = useAudioPlayerContext();

  const isThisItem =
    currentItem?.content_type === contentType &&
    currentItem?.content_id === contentId;

  const effectiveStatus = isThisItem ? status : "idle";

  const handleClick = useCallback(async () => {
    if (effectiveStatus === "playing") {
      pause();
      return;
    }
    if (effectiveStatus === "paused") {
      resume();
      return;
    }
    // idle or loading another item -> play this item
    await play({
      content_type: contentType,
      content_id: contentId,
      title: title ?? `${contentType} #${contentId}`,
    });
  }, [effectiveStatus, contentType, contentId, title, play, pause, resume]);

  const label = {
    idle: "Listen",
    loading: "Loading...",
    playing: "Pause",
    paused: "Resume",
  }[effectiveStatus];

  const icon = {
    idle: "\u25B6",
    loading: "\u25CF",
    playing: "\u275A\u275A",
    paused: "\u25B6",
  }[effectiveStatus];

  return (
    <button
      onClick={handleClick}
      disabled={effectiveStatus === "loading"}
      className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 transition-colors"
      title={effectiveStatus === "idle" ? "Listen to this content" : label}
    >
      <span className="text-xs">{icon}</span>
      {label}
    </button>
  );
}
