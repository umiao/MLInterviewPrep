import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../utils/api";
import { useToast } from "../../contexts/ToastContext";

export type GoldenItemType =
  | "framework_node"
  | "behavioral_example"
  | "company_document";

interface GoldenToggleButtonProps {
  itemType: GoldenItemType;
  itemId: number;
  isGolden: boolean;
  /** Required when itemType === "company_document" (PUT path nests under the company). */
  companyId?: number;
  /** Icon-only 32x32 square, or a pill with label. */
  variant?: "icon" | "pill";
  className?: string;
}

function buildEndpoint(
  itemType: GoldenItemType,
  itemId: number,
  companyId?: number,
): string {
  switch (itemType) {
    case "framework_node":
      return `/framework/nodes/${itemId}`;
    case "behavioral_example":
      return `/behavioral/examples/${itemId}`;
    case "company_document":
      if (companyId === undefined) {
        throw new Error(
          "GoldenToggleButton: companyId is required for company_document",
        );
      }
      return `/companies/${companyId}/documents/${itemId}`;
  }
}

function invalidationKeys(
  itemType: GoldenItemType,
  itemId: number,
  companyId?: number,
): Array<readonly unknown[]> {
  switch (itemType) {
    case "framework_node":
      return [
        ["framework", "tree"],
        ["framework", "node", itemId],
      ];
    case "behavioral_example":
      return [
        ["behavioral", "examples"],
        ["behavioral", "example", itemId],
        // Existing behavioral consumers use a hyphenated key; cover them too.
        ["behavioral-examples"],
        ["behavioral-examples-theme"],
      ];
    case "company_document":
      return [
        ["companies", companyId],
        ["companies", "document", itemId],
      ];
  }
}

function StarIcon({ filled }: { filled: boolean }) {
  return (
    <svg
      viewBox="0 0 24 24"
      width="20"
      height="20"
      fill={filled ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth={filled ? 0 : 2}
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 2.5l2.9 6.3 6.9.7-5.2 4.7 1.5 6.8L12 17.7l-6.1 3.3 1.5-6.8L2.2 9.5l6.9-.7L12 2.5z" />
    </svg>
  );
}

/**
 * Shared toggle for the is_golden curation flag across framework_node,
 * behavioral_example, and company_document items. Optimistically flips the
 * icon, then invalidates the relevant react-query caches on success; reverts
 * on error with a toast.
 */
export default function GoldenToggleButton({
  itemType,
  itemId,
  isGolden,
  companyId,
  variant = "icon",
  className = "",
}: GoldenToggleButtonProps) {
  // Optimistic override: only set while a mutation is pending. When undefined,
  // we fall back to the prop (which follows react-query cache after invalidation).
  const [pending, setPending] = useState<boolean | null>(null);
  const queryClient = useQueryClient();
  const toast = useToast();

  const mutation = useMutation({
    mutationFn: async (next: boolean) => {
      const endpoint = buildEndpoint(itemType, itemId, companyId);
      await api.put(endpoint, { is_golden: next });
      return next;
    },
    onMutate: (next: boolean) => {
      setPending(next);
    },
    onSuccess: (next: boolean) => {
      for (const key of invalidationKeys(itemType, itemId, companyId)) {
        queryClient.invalidateQueries({ queryKey: key });
      }
      toast.success(next ? "Marked as golden" : "Removed golden mark");
    },
    onError: () => {
      toast.error("Failed to update golden mark");
    },
    onSettled: () => {
      setPending(null);
    },
  });

  const active = pending ?? isGolden;
  const disabled = mutation.isPending;
  const label = active ? "Remove golden mark" : "Mark as golden";
  const colorClass = active
    ? "text-orange-500"
    : "text-gray-300 hover:text-gray-400";

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!disabled) mutation.mutate(!active);
  };

  if (variant === "pill") {
    const pillBg = active
      ? "bg-orange-50 border-orange-300"
      : "bg-white border-gray-200 hover:border-gray-300";
    return (
      <button
        type="button"
        onClick={handleClick}
        disabled={disabled}
        aria-pressed={active}
        title={label}
        className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-full border transition-colors disabled:opacity-60 ${pillBg} ${colorClass} ${className}`}
      >
        <StarIcon filled={active} />
        <span
          className={active ? "text-orange-700 font-medium" : "text-gray-600"}
        >
          {active ? "Golden" : "Mark as golden"}
        </span>
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled}
      aria-label={label}
      aria-pressed={active}
      title={label}
      className={`inline-flex items-center justify-center w-8 h-8 rounded transition-colors disabled:opacity-60 ${colorClass} ${className}`}
    >
      <StarIcon filled={active} />
    </button>
  );
}
