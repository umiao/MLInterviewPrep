import type { FacetTag } from "../../types/behavioral";

/**
 * Render a row of facet pills (small, distinct color from theme pills) for an
 * example or question. Facets are narrow staff-signal / cross-theme tags such
 * as "fast_learning" or "scrappy_innovation"; rendering nothing when the list
 * is empty keeps callers from having to do a length check.
 */
export default function FacetPills({
  facets,
  className = "",
}: {
  facets: FacetTag[] | undefined;
  className?: string;
}) {
  if (!facets || facets.length === 0) return null;
  return (
    <div className={"flex flex-wrap gap-1 " + className}>
      {facets.map((f) => (
        <span
          key={f.slug}
          title={f.label}
          className="text-[10px] px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 font-medium"
        >
          {f.label}
        </span>
      ))}
    </div>
  );
}
