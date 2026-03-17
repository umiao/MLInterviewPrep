import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import AudioPlayerBar from "./AudioPlayerBar";
import ErrorBoundary from "./ErrorBoundary";
import { useAudioPlayerContext } from "../contexts/AudioPlayerContext";

export default function Layout() {
  const { status } = useAudioPlayerContext();
  const isPlayerVisible = status !== "idle";

  return (
    <div className="flex min-h-screen w-full">
      <Sidebar />
      <main className={`flex-1 p-6 bg-gray-50 overflow-auto ${isPlayerVisible ? "pb-22" : ""}`}>
        <ErrorBoundary fallbackMessage="This page encountered an error.">
          <Outlet />
        </ErrorBoundary>
      </main>
      <ErrorBoundary fallbackMessage="Audio player encountered an error.">
        <AudioPlayerBar />
      </ErrorBoundary>
    </div>
  );
}
