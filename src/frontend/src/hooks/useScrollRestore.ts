import { useRef, useLayoutEffect, type RefObject } from "react";

/**
 * Preserves scroll position (as a ratio) across mode switches.
 *
 * Dual-ref design: preview mode scrolls the outer container, edit mode scrolls
 * the textarea internally. The hook picks the correct element based on mode.
 *
 * Call `captureScroll()` before changing mode to snapshot the current ratio,
 * then useLayoutEffect + rAF restores it on the new target after React commits.
 */
export function useScrollRestore(
  containerRef: RefObject<HTMLElement | null>,
  textareaRef: RefObject<HTMLTextAreaElement | null>,
  mode: string,
): {
  captureScroll: () => void;
} {
  const ratioRef = useRef(0);
  const hasCapturedRef = useRef(false);

  function getScrollTarget(m: string): HTMLElement | null {
    return m === "edit" ? textareaRef.current : containerRef.current;
  }

  function captureScroll(): void {
    const el = getScrollTarget(mode);
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

    const ratio = ratioRef.current;

    function applyScroll(): void {
      const el = getScrollTarget(mode);
      if (!el) return;
      const maxScroll = el.scrollHeight - el.clientHeight;
      if (maxScroll <= 0) return;
      el.scrollTop = ratio * maxScroll;
    }

    // rAF lets the browser finish layout after React commits.
    const rafId = requestAnimationFrame(applyScroll);

    // For preview mode, markdown rendering may be async (images, syntax
    // highlighting). Apply again after a short delay as a fallback.
    let timeoutId: ReturnType<typeof setTimeout> | undefined;
    if (mode === "preview") {
      timeoutId = setTimeout(applyScroll, 100);
    }

    return () => {
      cancelAnimationFrame(rafId);
      if (timeoutId !== undefined) clearTimeout(timeoutId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode]);

  return { captureScroll };
}
