interface SkeletonProps {
  /** CSS class for width/height. Defaults to "h-4 w-full". */
  className?: string;
}

/** Animated placeholder block for loading states. */
export default function Skeleton({ className = "h-4 w-full" }: SkeletonProps) {
  return (
    <div
      className={`animate-pulse rounded bg-gray-200 ${className}`}
      role="status"
      aria-label="Loading"
    />
  );
}
