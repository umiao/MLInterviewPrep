import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Problems from "./pages/Problems";
import Framework from "./pages/Framework";
import Questions from "./pages/Questions";
import Companies from "./pages/Companies";

export default function App() {
  return (
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
  );
}
