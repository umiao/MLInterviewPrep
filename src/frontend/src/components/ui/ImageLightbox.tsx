import { useState, useEffect, useCallback } from "react";

interface ImageLightboxProps {
  src: string;
  alt: string;
  className?: string;
}

/**
 * Image that opens a fullscreen lightbox overlay on click.
 * Click backdrop or press Escape to close.
 */
export default function ImageLightbox({ src, alt, className }: ImageLightboxProps) {
  const [open, setOpen] = useState(false);

  const close = useCallback(() => setOpen(false), []);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, close]);

  return (
    <>
      <img
        src={src}
        alt={alt}
        className={`${className ?? ""} cursor-pointer`}
        onClick={(e) => {
          e.stopPropagation();
          setOpen(true);
        }}
      />
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80"
          onClick={close}
        >
          <img
            src={src}
            alt={alt}
            className="max-w-[95vw] max-h-[95vh] object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
}
