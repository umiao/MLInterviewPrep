import { useRef, useLayoutEffect, type RefObject } from "react";

/**
 * Captures scroll position (as a ratio) before a mode switch and restores it
 * after the new content renders. Uses ResizeObserver to wait for layout to
 * stabilize, with a 500ms timeout fallback.
 */
export function useScrollRestore(
  scrollContainerRef: RefObject<HTMLElement | null>,
  mode: string,
): {
  captureScroll: () => void;
} {
  const ratioRef = useRef(0);
  const hasCapturedRef = useRef(false);

  function captureScroll(): void {
    const el = scrollContainerRef.current;
    if (!el) return;
    const maxScroll = el.scrollHeight - el.clientHeight;
    if (maxScroll <= 0) {
      ratioRef.current = 0;
    } else {
      ratioRef.current = el.scrollTop / maxScroll;
    }
    hasCapturedRef.current = true;
  }

  useLayoutEffect(() => {
    if (!hasCapturedRef.current) return;
    hasCapturedRef.current = false;

    const el = scrollContainerRef.current;
    if (!el) return;

    const ratio = ratioRef.current;

    function applyScroll(): void {
      if (!el) return;
      const maxScroll = el.scrollHeight - el.clientHeight;
      if (maxScroll <= 0) return;
      el.scrollTop = ratio * maxScroll;
    }

    // Observe first child for size changes to detect when content has laid out.
    const target = el.firstElementChild ?? el;
    let lastHeight = target.getBoundingClientRect().height;
    let stableTimer: ReturnType<typeof setTimeout> | null = null;
    let fallbackTimer: ReturnType<typeof setTimeout> | null = null;

    const observer = new ResizeObserver(() => {
      const h = target.getBoundingClientRect().height;
      if (h !== lastHeight) {
        lastHeight = h;
        if (stableTimer) clearTimeout(stableTimer);
        stableTimer = setTimeout(() => {
          applyScroll();
          cleanup();
        }, 50);
      }
    });

    function cleanup(): void {
      observer.disconnect();
      if (stableTimer) clearTimeout(stableTimer);
      if (fallbackTimer) clearTimeout(fallbackTimer);
    }

    observer.observe(target);

    // Apply immediately in case content is already stable (e.g. textarea).
    requestAnimationFrame(applyScroll);

    // Fallback: if ResizeObserver never fires (content same size), apply after 500ms.
    fallbackTimer = setTimeout(() => {
      applyScroll();
      cleanup();
    }, 500);

    return cleanup;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode]);

  return { captureScroll };
}
