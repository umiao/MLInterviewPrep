interface BadgeProps {
  children: string;
  variant?: "blue" | "green" | "yellow" | "red" | "gray" | "purple";
  className?: string;
}

const VARIANTS: Record<string, string> = {
  blue: "bg-blue-100 text-blue-700",
  green: "bg-green-100 text-green-700",
  yellow: "bg-yellow-100 text-yellow-700",
  red: "bg-red-100 text-red-700",
  gray: "bg-gray-100 text-gray-600",
  purple: "bg-purple-100 text-purple-700",
};

export default function Badge({
  children,
  variant = "gray",
  className = "",
}: BadgeProps) {
  return (
    <span
      className={`text-xs px-1.5 py-0.5 rounded inline-block ${VARIANTS[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
