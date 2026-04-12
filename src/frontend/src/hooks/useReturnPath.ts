import { useSearchParams } from "react-router-dom";

export function useReturnPath(defaultPath: string): string {
  const [params] = useSearchParams();
  const from = params.get("from");
  if (from === "quick-index") return "/quick-index?section=bq";
  return defaultPath;
}
