import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Problems from "./pages/Problems";
import Framework from "./pages/Framework";
import Questions from "./pages/Questions";
import Companies from "./pages/Companies";

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
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="problems" element={<Problems />} />
            <Route path="framework" element={<Framework />} />
            <Route path="questions" element={<Questions />} />
            <Route path="companies" element={<Companies />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
