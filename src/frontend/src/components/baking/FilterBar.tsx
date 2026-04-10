import { useState, useEffect } from "react";
import type { CakeType, CakeSize, CakeFormat, RecipeFilters } from "../../types/baking";

interface FilterBarProps {
  filters: RecipeFilters;
  onFilterChange: (filters: RecipeFilters) => void;
}

const CAKE_TYPES: { value: CakeType | "all"; label: string }[] = [
  { value: "all", label: "All" },
  { value: "basque", label: "Basque" },
  { value: "cheesecake", label: "Cheesecake" },
  { value: "chiffon", label: "Chiffon" },
  { value: "cream_cake", label: "Cream Cake" },
];

const SIZES: { value: CakeSize; label: string }[] = [
  { value: "4inch", label: "4-inch" },
  { value: "6inch", label: "6-inch" },
];

const FORMATS: { value: CakeFormat | "all"; label: string }[] = [
  { value: "all", label: "All" },
  { value: "full", label: "Full" },
  { value: "box", label: "Box" },
];

export default function FilterBar({ filters, onFilterChange }: FilterBarProps) {
  const [localType, setLocalType] = useState<CakeType | "all">(filters.cake_type ?? "all");
  const [selectedSizes, setSelectedSizes] = useState<Set<CakeSize>>(
    () => new Set(filters.sizes ?? [])
  );
  const [localFormat, setLocalFormat] = useState<CakeFormat | "all">(filters.format ?? "all");

  useEffect(() => {
    onFilterChange({
      cake_type: localType === "all" ? undefined : localType,
      sizes: selectedSizes.size > 0 ? [...selectedSizes] : undefined,
      format: localFormat === "all" ? undefined : localFormat,
    });
  }, [localType, selectedSizes, localFormat]);

  const handleSizeToggle = (size: CakeSize) => {
    setSelectedSizes((prev) => {
      const next = new Set(prev);
      if (next.has(size)) {
        next.delete(size);
      } else {
        next.add(size);
      }
      return next;
    });
  };

  const handleAllSizes = () => {
    setSelectedSizes(new Set());
  };

  const allSelected = selectedSizes.size === 0;

  return (
    <div className="space-y-3 rounded-xl bg-amber-50/50 p-4 border border-amber-100">
      {/* Row 1: Cake type chips */}
      <div className="flex flex-wrap gap-2">
        {CAKE_TYPES.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => setLocalType(value)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              localType === value
                ? "bg-amber-600 text-white shadow-sm"
                : "bg-white text-amber-800 border border-amber-200 hover:bg-amber-100"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Row 2: Size + Format toggles */}
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-amber-700 font-medium">Size:</span>
          <div className="flex rounded-lg overflow-hidden border border-amber-200">
            <button
              onClick={handleAllSizes}
              className={`px-3 py-1 text-sm transition-colors ${
                allSelected
                  ? "bg-amber-600 text-white"
                  : "bg-white text-amber-800 hover:bg-amber-50"
              }`}
            >
              All
            </button>
            {SIZES.map(({ value, label }) => (
              <button
                key={value}
                onClick={() => handleSizeToggle(value)}
                className={`px-3 py-1 text-sm transition-colors ${
                  selectedSizes.has(value)
                    ? "bg-amber-600 text-white"
                    : "bg-white text-amber-800 hover:bg-amber-50"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
          {selectedSizes.size > 1 && (
            <span className="text-xs text-amber-600 font-medium">
              Combined
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-amber-700 font-medium">Format:</span>
          <div className="flex rounded-lg overflow-hidden border border-amber-200">
            {FORMATS.map(({ value, label }) => (
              <button
                key={value}
                onClick={() => setLocalFormat(value)}
                className={`px-3 py-1 text-sm transition-colors ${
                  localFormat === value
                    ? "bg-amber-600 text-white"
                    : "bg-white text-amber-800 hover:bg-amber-50"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
