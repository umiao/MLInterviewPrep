import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import AudioPlayerBar from "./AudioPlayerBar";
import { useAudioPlayerContext } from "../contexts/AudioPlayerContext";

export default function Layout() {
  const { status } = useAudioPlayerContext();
  const isPlayerVisible = status !== "idle";

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className={`flex-1 p-6 bg-gray-50 overflow-auto ${isPlayerVisible ? "pb-22" : ""}`}>
        <Outlet />
      </main>
      <AudioPlayerBar />
    </div>
  );
}
