interface LoadingSpinnerProps {
  /** Text shown below the spinner. Defaults to "Loading..." */
  message?: string;
  /** Size variant. Defaults to "md" */
  size?: "sm" | "md" | "lg";
  /** If true, renders as a full-height centered block (for page-level loading). */
  fullHeight?: boolean;
}

const SIZES = {
  sm: "h-4 w-4 border-2",
  md: "h-8 w-8 border-2",
  lg: "h-12 w-12 border-3",
} as const;

/** Animated spinner with optional message, used for React Query loading states. */
export default function LoadingSpinner({
  message = "Loading...",
  size = "md",
  fullHeight = false,
}: LoadingSpinnerProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center gap-2 text-gray-400 ${
        fullHeight ? "h-64" : "py-8"
      }`}
      role="status"
      aria-label={message}
    >
      <div
        className={`${SIZES[size]} rounded-full border-gray-300 border-t-blue-500 animate-spin`}
      />
      {message && <span className="text-sm">{message}</span>}
    </div>
  );
}
