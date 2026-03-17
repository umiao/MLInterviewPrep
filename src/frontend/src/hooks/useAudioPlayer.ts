/**
 * Core audio player hook -- manages HTML5 Audio element for TTS playback.
 *
 * Handles: play/pause/resume/skip, auto-advance (radio mode), playback speed,
 * progress tracking with periodic backend saves.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../utils/api";
import type {
  AudioPlayerItem,
  PlayerStatus,
  QueueItem,
  QueueResponse,
  SynthesizeAsyncResponse,
  SynthesizeResponse,
} from "../types/reading";

const PROGRESS_SAVE_INTERVAL_MS = 30_000;
const JOB_POLL_INTERVAL_MS = 1_500;
const JOB_POLL_MAX_ATTEMPTS = 120; // ~3 minutes max
const SPEED_OPTIONS = [0.75, 1, 1.25, 1.5, 1.75, 2] as const;
export type PlaybackSpeed = (typeof SPEED_OPTIONS)[number];
export { SPEED_OPTIONS };

export interface AudioPlayerState {
  /** Current player status. */
  status: PlayerStatus;
  /** Currently playing item, if any. */
  currentItem: AudioPlayerItem | null;
  /** Playback queue for radio mode. */
  queue: AudioPlayerItem[];
  /** Current position in seconds. */
  currentTime: number;
  /** Total duration in seconds. */
  duration: number;
  /** Playback speed multiplier. */
  speed: PlaybackSpeed;
  /** Whether radio mode auto-advances through queue. */
  autoAdvance: boolean;
  /** Error message, if any. */
  error: string | null;
}

export interface AudioPlayerActions {
  /** Start playing a specific item. */
  play: (item: AudioPlayerItem) => Promise<void>;
  /** Pause the current playback. */
  pause: () => void;
  /** Resume paused playback. */
  resume: () => void;
  /** Toggle play/pause. */
  togglePlayPause: () => void;
  /** Skip to next item in queue. */
  skipNext: () => void;
  /** Skip to previous item (restart current if >3s in). */
  skipPrev: () => void;
  /** Set playback speed. */
  setSpeed: (speed: PlaybackSpeed) => void;
  /** Enable/disable auto-advance (radio mode). */
  setAutoAdvance: (enabled: boolean) => void;
  /** Load a queue of items and start playing the first one. Returns true on success. */
  startRadio: (items?: AudioPlayerItem[]) => Promise<boolean>;
  /** Stop playback and clear state. */
  stop: () => void;
  /** Seek to a position (0-1 fraction). */
  seek: (fraction: number) => void;
}

export type UseAudioPlayerReturn = AudioPlayerState & AudioPlayerActions;

export function useAudioPlayer(): UseAudioPlayerReturn {
  const [status, setStatus] = useState<PlayerStatus>("idle");
  const [currentItem, setCurrentItem] = useState<AudioPlayerItem | null>(null);
  const [queue, setQueue] = useState<AudioPlayerItem[]>([]);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [speed, setSpeedState] = useState<PlaybackSpeed>(1);
  const [autoAdvance, setAutoAdvance] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const progressTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const queueIndexRef = useRef(-1);
  // Refs to track current values in callbacks without stale closures
  const queueRef = useRef<AudioPlayerItem[]>([]);
  const autoAdvanceRef = useRef(false);
  // Browser SpeechSynthesis tracking
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const isBrowserTTSRef = useRef(false);
  // Prefetch cache: maps "content_type:content_id" to the synthesize response
  const prefetchCacheRef = useRef<Map<string, SynthesizeResponse>>(new Map());

  // Keep refs in sync with state
  useEffect(() => {
    queueRef.current = queue;
  }, [queue]);
  useEffect(() => {
    autoAdvanceRef.current = autoAdvance;
  }, [autoAdvance]);

  /** Save progress to backend. */
  const saveProgress = useCallback(
    async (item: AudioPlayerItem, time: number, dur: number) => {
      if (dur <= 0) return;
      const fraction = time / dur;
      const charOffset = Math.round(fraction * 1000); // approximate
      try {
        await api.put(
          `/reading/progress/${item.content_type}/${item.content_id}`,
          {
            last_chunk_index: 0,
            char_offset: charOffset,
            total_chars: 1000,
            completed: fraction >= 0.95,
          },
        );
      } catch {
        // Silent fail for progress saves
      }
    },
    [],
  );

  /** Start periodic progress saving. */
  const startProgressTimer = useCallback(
    (item: AudioPlayerItem) => {
      if (progressTimerRef.current) {
        clearInterval(progressTimerRef.current);
      }
      progressTimerRef.current = setInterval(() => {
        const audio = audioRef.current;
        if (audio && !audio.paused) {
          saveProgress(item, audio.currentTime, audio.duration);
        }
      }, PROGRESS_SAVE_INTERVAL_MS);
    },
    [saveProgress],
  );

  /** Stop progress timer. */
  const stopProgressTimer = useCallback(() => {
    if (progressTimerRef.current) {
      clearInterval(progressTimerRef.current);
      progressTimerRef.current = null;
    }
  }, []);

  /** Clean up audio element and browser TTS. */
  const cleanupAudio = useCallback(() => {
    if (isBrowserTTSRef.current) {
      window.speechSynthesis.cancel();
      utteranceRef.current = null;
      isBrowserTTSRef.current = false;
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.removeAttribute("src");
      audioRef.current.load();
      audioRef.current = null;
    }
    stopProgressTimer();
  }, [stopProgressTimer]);

  /** Build cache key for prefetch map. */
  const cacheKey = useCallback(
    (item: AudioPlayerItem) => `${item.content_type}:${item.content_id}`,
    [],
  );

  /** Prefetch the next item in queue (if any). */
  const prefetchNext = useCallback(
    async (currentIdx: number) => {
      const q = queueRef.current;
      const nextIdx = currentIdx + 1;
      if (nextIdx >= q.length) return; // no next item
      const nextItem = q[nextIdx];
      const key = cacheKey(nextItem);
      if (prefetchCacheRef.current.has(key)) return; // already prefetched

      try {
        const raw = await api.post<SynthesizeResponse & Partial<SynthesizeAsyncResponse>>(
          "/reading/synthesize",
          {
            content_type: nextItem.content_type,
            content_id: nextItem.content_id,
          },
        );

        if (raw.job_id) {
          // Async synthesis -- poll until complete for prefetch
          let attempts = 0;
          while (attempts < JOB_POLL_MAX_ATTEMPTS) {
            await new Promise((r) => setTimeout(r, JOB_POLL_INTERVAL_MS));
            attempts++;
            const job = await api.get<{
              job_id: string;
              status: string;
              audio_url: string | null;
              error: string | null;
              mode?: string;
              text?: string;
            }>(`/reading/jobs/${raw.job_id}`);
            if (job.status === "completed") {
              if (job.mode === "browser" && job.text) {
                prefetchCacheRef.current.set(key, { mode: "browser", text: job.text, audio_url: null, cache_hit: false, content_length: 0 });
              } else if (job.audio_url) {
                prefetchCacheRef.current.set(key, { mode: "file", audio_url: job.audio_url, text: null, cache_hit: false, content_length: 0 });
              }
              break;
            } else if (job.status === "failed") {
              break;
            }
          }
        } else {
          prefetchCacheRef.current.set(key, raw as SynthesizeResponse);
        }
      } catch {
        // Silent fail for prefetch -- will synthesize on demand
      }
    },
    [cacheKey],
  );

  /** Stop everything. */
  const stop = useCallback(() => {
    cleanupAudio();
    prefetchCacheRef.current.clear();
    setStatus("idle");
    setCurrentItem(null);
    setCurrentTime(0);
    setDuration(0);
    setError(null);
    queueIndexRef.current = -1;
  }, [cleanupAudio]);

  /** Play a specific item. */
  const play = useCallback(
    async (item: AudioPlayerItem) => {
      cleanupAudio();
      setError(null);
      setCurrentItem(item);
      setStatus("loading");

      try {
        // Check prefetch cache first
        const key = cacheKey(item);
        let response = prefetchCacheRef.current.get(key) ?? null;
        if (response) {
          prefetchCacheRef.current.delete(key);
        } else {
          // The backend may return 200 (SynthesizeResponse) or 202 (SynthesizeAsyncResponse).
          // Both are treated as OK by the fetch wrapper, so we check for job_id to distinguish.
          const raw = await api.post<SynthesizeResponse & Partial<SynthesizeAsyncResponse>>(
            "/reading/synthesize",
            {
              content_type: item.content_type,
              content_id: item.content_id,
            },
          );

          if (raw.job_id) {
            // Async synthesis -- poll until complete
            let attempts = 0;
            while (attempts < JOB_POLL_MAX_ATTEMPTS) {
              await new Promise((r) => setTimeout(r, JOB_POLL_INTERVAL_MS));
              attempts++;
              const job = await api.get<{
                job_id: string;
                status: string;
                audio_url: string | null;
                error: string | null;
                mode?: string;
                text?: string;
              }>(`/reading/jobs/${raw.job_id}`);

              if (job.status === "completed") {
                if (job.mode === "browser" && job.text) {
                  response = { mode: "browser", text: job.text, audio_url: null, cache_hit: false, content_length: 0 };
                } else if (job.audio_url) {
                  response = { mode: "file", audio_url: job.audio_url, text: null, cache_hit: false, content_length: 0 };
                } else {
                  throw new Error("Job completed but no audio returned");
                }
                break;
              } else if (job.status === "failed") {
                throw new Error(job.error || "Audio synthesis failed");
              }
              // else still pending -- continue polling
            }
            if (!response) {
              throw new Error("Audio synthesis timed out");
            }
          } else {
            response = raw as SynthesizeResponse;
          }
        }

        if (response.mode === "browser" && response.text) {
          // Browser TTS fallback -- use SpeechSynthesis API
          if (!("speechSynthesis" in window)) {
            throw new Error("Browser speech synthesis not available");
          }
          isBrowserTTSRef.current = true;
          const utterance = new SpeechSynthesisUtterance(response.text);
          utterance.rate = speed;
          utteranceRef.current = utterance;
          utterance.onend = () => {
            isBrowserTTSRef.current = false;
            utteranceRef.current = null;
            setCurrentTime(0);
            setDuration(0);
            // Auto-advance if in radio mode
            if (autoAdvanceRef.current && queueRef.current.length > 0) {
              const nextIdx = queueIndexRef.current + 1;
              if (nextIdx < queueRef.current.length) {
                queueIndexRef.current = nextIdx;
                play(queueRef.current[nextIdx]);
                return;
              }
            }
            setStatus("idle");
            setCurrentItem(null);
          };
          utterance.onerror = () => {
            isBrowserTTSRef.current = false;
            utteranceRef.current = null;
            setError("Browser speech synthesis failed");
            setStatus("idle");
          };
          window.speechSynthesis.speak(utterance);
          setStatus("playing");
          // Prefetch next item while browser TTS plays
          prefetchNext(queueIndexRef.current);
          return;
        }

        if (!response.audio_url) {
          throw new Error("No audio URL returned from synthesis");
        }

        const audio = new Audio(response.audio_url);
        audio.playbackRate = speed;
        audioRef.current = audio;

        audio.ontimeupdate = () => {
          setCurrentTime(audio.currentTime);
        };

        audio.onloadedmetadata = () => {
          setDuration(audio.duration);
        };

        audio.onended = () => {
          // Save final progress
          saveProgress(item, audio.duration, audio.duration);
          stopProgressTimer();

          // Auto-advance in radio mode
          if (autoAdvanceRef.current && queueRef.current.length > 0) {
            const nextIdx = queueIndexRef.current + 1;
            if (nextIdx < queueRef.current.length) {
              queueIndexRef.current = nextIdx;
              play(queueRef.current[nextIdx]);
              return;
            }
          }

          setStatus("idle");
          setCurrentItem(null);
          setCurrentTime(0);
          setDuration(0);
        };

        audio.onerror = () => {
          setError("Audio playback error");
          setStatus("idle");
          setCurrentItem(null);
          stopProgressTimer();
        };

        await audio.play();
        setStatus("playing");
        startProgressTimer(item);
        // Prefetch next item while current plays
        prefetchNext(queueIndexRef.current);
      } catch (err) {
        const msg =
          err instanceof DOMException && err.name === "NotAllowedError"
            ? "Autoplay blocked -- click play to start"
            : err instanceof Error
              ? err.message
              : "Failed to synthesize";
        setError(msg);
        setStatus("idle");
        setCurrentItem(null);
      }
    },
    [
      cleanupAudio,
      cacheKey,
      speed,
      saveProgress,
      stopProgressTimer,
      startProgressTimer,
      prefetchNext,
    ],
  );

  /** Pause playback. */
  const pause = useCallback(() => {
    if (status !== "playing") return;
    if (isBrowserTTSRef.current) {
      window.speechSynthesis.pause();
      setStatus("paused");
    } else if (audioRef.current) {
      audioRef.current.pause();
      setStatus("paused");
    }
  }, [status]);

  /** Resume playback. */
  const resume = useCallback(() => {
    if (status !== "paused") return;
    if (isBrowserTTSRef.current) {
      window.speechSynthesis.resume();
      setStatus("playing");
    } else if (audioRef.current) {
      audioRef.current.play();
      setStatus("playing");
    }
  }, [status]);

  /** Toggle play/pause. */
  const togglePlayPause = useCallback(() => {
    if (status === "playing") {
      pause();
    } else if (status === "paused") {
      resume();
    }
  }, [status, pause, resume]);

  /** Skip to next item in queue. */
  const skipNext = useCallback(() => {
    if (queue.length === 0) return;
    const nextIdx = queueIndexRef.current + 1;
    if (nextIdx < queue.length) {
      queueIndexRef.current = nextIdx;
      play(queue[nextIdx]);
    }
  }, [queue, play]);

  /** Skip to previous (restart current if >3s in, else go prev). */
  const skipPrev = useCallback(() => {
    if (audioRef.current && audioRef.current.currentTime > 3) {
      audioRef.current.currentTime = 0;
      setCurrentTime(0);
      return;
    }
    if (queue.length === 0) return;
    const prevIdx = queueIndexRef.current - 1;
    if (prevIdx >= 0) {
      queueIndexRef.current = prevIdx;
      play(queue[prevIdx]);
    }
  }, [queue, play]);

  /** Set playback speed. */
  const setSpeed = useCallback(
    (newSpeed: PlaybackSpeed) => {
      setSpeedState(newSpeed);
      if (audioRef.current) {
        audioRef.current.playbackRate = newSpeed;
      }
    },
    [],
  );

  /** Enable/disable auto-advance. */
  const setAutoAdvanceState = useCallback((enabled: boolean) => {
    setAutoAdvance(enabled);
  }, []);

  /** Load queue from backend and start radio mode. Returns true on success. */
  const startRadio = useCallback(
    async (items?: AudioPlayerItem[]): Promise<boolean> => {
      // Guard: prevent concurrent startRadio calls
      if (status === "loading") return false;
      setAutoAdvance(true);
      setError(null);
      prefetchCacheRef.current.clear();

      let radioQueue: AudioPlayerItem[];
      if (items && items.length > 0) {
        radioQueue = items;
      } else {
        try {
          const response = await api.get<QueueResponse>("/reading/queue");
          radioQueue = response.items
            .filter((qi: QueueItem) => !qi.completed)
            .map((qi: QueueItem) => ({
              content_type: qi.content_type,
              content_id: qi.content_id,
              title: qi.title,
            }));
        } catch (err) {
          setError(
            err instanceof Error ? err.message : "Failed to load queue",
          );
          return false;
        }
      }

      if (radioQueue.length === 0) {
        setError("empty:No pending items in your study queue");
        return false;
      }

      setQueue(radioQueue);
      queueRef.current = radioQueue;
      queueIndexRef.current = 0;
      try {
        await play(radioQueue[0]);
        return true;
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to start radio");
        setStatus("idle");
        return false;
      }
    },
    [play, status],
  );

  /** Seek to a fraction (0-1) of the track. */
  const seek = useCallback((fraction: number) => {
    if (audioRef.current && audioRef.current.duration) {
      const clampedFraction = Math.max(0, Math.min(1, fraction));
      audioRef.current.currentTime = clampedFraction * audioRef.current.duration;
      setCurrentTime(audioRef.current.currentTime);
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanupAudio();
    };
  }, [cleanupAudio]);

  return {
    status,
    currentItem,
    queue,
    currentTime,
    duration,
    speed,
    autoAdvance,
    error,
    play,
    pause,
    resume,
    togglePlayPause,
    skipNext,
    skipPrev,
    setSpeed,
    setAutoAdvance: setAutoAdvanceState,
    startRadio,
    stop,
    seek,
  };
}
