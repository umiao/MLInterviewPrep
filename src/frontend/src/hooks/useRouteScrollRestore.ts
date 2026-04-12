import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const STORAGE_PREFIX = "scroll:";

export function useRouteScrollRestore(): void {
  const location = useLocation();
  const storageKey = STORAGE_PREFIX + location.key;

  useEffect(() => {
    const onScroll = () => {
      sessionStorage.setItem(storageKey, String(window.scrollY));
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [storageKey]);

  useEffect(() => {
    const stored = sessionStorage.getItem(storageKey);
    if (stored !== null) {
      requestAnimationFrame(() => window.scrollTo(0, parseInt(stored, 10)));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
}
