import { useState, useCallback } from "react";
import type { BakingRecipe, CakeSize } from "../../types/baking";
import IngredientTable from "./IngredientTable";
import ScalingCalculator from "./ScalingCalculator";

interface RecipeDetailProps {
  recipe: BakingRecipe;
  onClose: () => void;
  onDelete?: (id: number) => void;
  filterSizes?: CakeSize[];
}

const CATEGORY_STYLES: Record<string, string> = {
  complete: "bg-amber-100 text-amber-800",
  base: "bg-emerald-100 text-emerald-800",
  cream: "bg-pink-100 text-pink-800",
  decoration: "bg-violet-100 text-violet-800",
};

const SIZE_LABELS: Record<string, string> = {
  "4inch": "4-inch",
  "6inch": "6-inch",
  "8inch": "8-inch",
  universal: "Universal",
};

export default function RecipeDetail({
  recipe,
  onClose,
  onDelete,
  filterSizes,
}: RecipeDetailProps) {
  const [scaledAmounts, setScaledAmounts] = useState<Record<number, number>>(
    {}
  );

  const handleScaledAmounts = useCallback(
    (amounts: Record<number, number>) => {
      setScaledAmounts(amounts);
    },
    []
  );

  const hasScaling = Object.keys(scaledAmounts).length > 0;

  return (
    <div className="bg-white rounded-xl border border-amber-100 shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-amber-50 px-5 py-4 border-b border-amber-100">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h2 className="text-lg font-bold text-gray-900 truncate">
              {recipe.name}
            </h2>
            {recipe.name_zh && (
              <p className="text-sm text-gray-500 mt-0.5">{recipe.name_zh}</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="shrink-0 p-1 text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2 mt-3">
          <span
            className={`px-2 py-0.5 rounded-full text-xs font-medium ${
              CATEGORY_STYLES[recipe.category] ?? "bg-gray-100 text-gray-600"
            }`}
          >
            {recipe.category}
          </span>
          <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-700 text-xs font-medium border border-amber-200">
            {recipe.cake_type.replace("_", " ")}
          </span>
          {recipe.size !== "universal" && (
            <span className="px-2 py-0.5 rounded bg-gray-100 text-gray-600 text-xs font-medium">
              {SIZE_LABELS[recipe.size] ?? recipe.size}
            </span>
          )}
          {recipe.format === "box" && (
            <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 text-xs font-medium">
              Box format
            </span>
          )}
          {recipe.is_preset && (
            <span className="px-2 py-0.5 rounded bg-gray-50 text-gray-500 text-xs">
              Preset
            </span>
          )}
        </div>
      </div>

      {/* Body */}
      <div className="p-5 space-y-6">
        {/* Scaling Calculator */}
        <ScalingCalculator
          recipe={recipe}
          onScaledAmounts={handleScaledAmounts}
          filterSizes={filterSizes}
        />

        {/* Ingredients */}
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">
            Ingredients
            {hasScaling && (
              <span className="text-xs text-amber-600 font-normal ml-2">
                (scaled)
              </span>
            )}
          </h3>
          <IngredientTable
            ingredients={recipe.ingredients}
            scaledAmounts={hasScaling ? scaledAmounts : undefined}
          />
        </div>

        {/* Steps */}
        {recipe.steps && recipe.steps.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Steps</h3>
            <ol className="list-decimal list-inside space-y-1.5 text-sm text-gray-600">
              {recipe.steps.map((step, i) => (
                <li key={i} className="leading-relaxed">
                  {step}
                </li>
              ))}
            </ol>
          </div>
        )}

        {/* Notes */}
        {recipe.notes && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-1">Notes</h3>
            <p className="text-sm text-gray-500 whitespace-pre-line">
              {recipe.notes}
            </p>
          </div>
        )}

        {/* Delete (non-preset only) */}
        {!recipe.is_preset && onDelete && (
          <div className="pt-3 border-t border-gray-100">
            <button
              onClick={() => onDelete(recipe.id)}
              className="text-xs text-red-400 hover:text-red-600 transition-colors"
            >
              Delete recipe
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
