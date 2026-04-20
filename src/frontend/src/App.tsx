import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ToastProvider } from "./contexts/ToastContext";
import { AudioPlayerProvider } from "./contexts/AudioPlayerContext";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Problems from "./pages/Problems";
import Framework from "./pages/Framework";
import Questions from "./pages/Questions";
import Companies from "./pages/Companies";
import Settings from "./pages/Settings";
import Analytics from "./pages/Analytics";
import PrepNotesPage from "./pages/PrepNotesPage";
import ProblemDetailPage from "./pages/ProblemDetailPage";
import StudyRadio from "./pages/StudyRadio";
import FrameworkNotesPage from "./pages/FrameworkNotesPage";
import SystemDesignList from "./pages/SystemDesignList";
import SystemDesignDetail from "./pages/SystemDesignDetail";
import BehavioralQuestions from "./pages/BehavioralQuestions";
import BehavioralThemePage from "./pages/BehavioralThemePage";
import QuickIndex from "./pages/QuickIndex";
import MLFundamentals from "./pages/MLFundamentals";
import BakingStudio from "./pages/BakingStudio";
import KnowledgeGraph from "./pages/KnowledgeGraph";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <AudioPlayerProvider>
          <BrowserRouter>
            <Routes>
              <Route element={<Layout />}>
                <Route index element={<Dashboard />} />
                <Route path="quick-index" element={<QuickIndex />} />
                <Route path="ml-fundamentals" element={<MLFundamentals />} />
                <Route path="problems" element={<Problems />} />
                <Route path="problems/:problemId" element={<ProblemDetailPage />} />
                <Route path="framework" element={<Framework />} />
                <Route path="framework/:nodeId" element={<Framework />} />
                <Route path="framework/:nodeId/notes" element={<FrameworkNotesPage />} />
                <Route path="kg" element={<KnowledgeGraph />} />
                <Route path="system-design" element={<SystemDesignList />} />
                <Route path="system-design/:slug" element={<SystemDesignDetail />} />
                <Route path="behavioral" element={<BehavioralQuestions />} />
                <Route path="behavioral/theme/:slug" element={<BehavioralThemePage />} />
                <Route path="questions" element={<Questions />} />
                <Route path="companies" element={<Companies />} />
                <Route path="companies/:companyId/prep" element={<PrepNotesPage />} />
                <Route path="radio" element={<StudyRadio />} />
                <Route path="analytics" element={<Analytics />} />
                <Route path="settings" element={<Settings />} />
                <Route path="baking" element={<BakingStudio />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </AudioPlayerProvider>
      </ToastProvider>
    </QueryClientProvider>
  );
}
