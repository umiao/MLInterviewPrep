import { useCallback, useRef, useState } from "react";

interface ListenButtonProps {
  contentType: "framework_node";
  contentId: number;
}

/**
 * Button that synthesizes and plays TTS audio for a content item.
 * Manages its own audio element for play/pause/stop.
 */
export default function ListenButton({ contentType, contentId }: ListenButtonProps) {
  const [state, setState] = useState<"idle" | "loading" | "playing" | "paused">("idle");
  const [error, setError] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.src = "";
      audioRef.current = null;
    }
    setState("idle");
  }, []);

  const handleClick = useCallback(async () => {
    setError(null);

    // If playing -> pause
    if (state === "playing" && audioRef.current) {
      audioRef.current.pause();
      setState("paused");
      return;
    }

    // If paused -> resume
    if (state === "paused" && audioRef.current) {
      audioRef.current.play();
      setState("playing");
      return;
    }

    // If idle -> synthesize and play
    setState("loading");
    try {
      const res = await fetch("/api/reading/synthesize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content_type: contentType, content_id: contentId }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({ detail: "Synthesis failed" }));
        throw new Error(data.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      const audio = new Audio(data.audio_url);
      audioRef.current = audio;

      audio.onended = () => {
        setState("idle");
        audioRef.current = null;
      };
      audio.onerror = () => {
        setError("Audio playback error");
        setState("idle");
        audioRef.current = null;
      };

      await audio.play();
      setState("playing");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to synthesize");
      setState("idle");
    }
  }, [state, contentType, contentId]);

  const label = {
    idle: "Listen",
    loading: "Loading...",
    playing: "Pause",
    paused: "Resume",
  }[state];

  const icon = {
    idle: "\u25B6",       // play triangle
    loading: "\u25CF",    // circle (loading)
    playing: "\u275A\u275A", // pause bars
    paused: "\u25B6",     // play triangle
  }[state];

  return (
    <div>
      <div className="flex items-center gap-2">
        <button
          onClick={handleClick}
          disabled={state === "loading"}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 transition-colors"
          title={state === "idle" ? "Listen to this node's description" : label}
        >
          <span className="text-xs">{icon}</span>
          {label}
        </button>
        {state !== "idle" && state !== "loading" && (
          <button
            onClick={stop}
            className="px-2 py-1.5 text-sm text-gray-500 hover:text-red-600 transition-colors"
            title="Stop"
          >
            &#x25A0;
          </button>
        )}
      </div>
      {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
    </div>
  );
}
