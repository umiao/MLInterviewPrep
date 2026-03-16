/**
 * Global audio player context -- provides playback state and controls
 * to the entire app. Persists across route navigation.
 */
import { createContext, useContext } from "react";
import type { ReactNode } from "react";
import {
  useAudioPlayer,
  type UseAudioPlayerReturn,
} from "../hooks/useAudioPlayer";

const AudioPlayerContext = createContext<UseAudioPlayerReturn | null>(null);

export function AudioPlayerProvider({ children }: { children: ReactNode }) {
  const player = useAudioPlayer();

  return (
    <AudioPlayerContext.Provider value={player}>
      {children}
    </AudioPlayerContext.Provider>
  );
}

export function useAudioPlayerContext(): UseAudioPlayerReturn {
  const ctx = useContext(AudioPlayerContext);
  if (!ctx) {
    throw new Error(
      "useAudioPlayerContext must be used within an AudioPlayerProvider",
    );
  }
  return ctx;
}
