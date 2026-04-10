import { useState, useMemo, useEffect } from "react";
import type { BakingRecipe, BakingIngredient, CakeSize } from "../../types/baking";

interface ScalingCalculatorProps {
  recipe: BakingRecipe;
  onScaledAmounts: (amounts: Record<number, number>) => void;
  /** Sizes selected in FilterBar -- when multiple, auto-enable multi-size summing */
  filterSizes?: CakeSize[];
}

const SIZE_RATIOS: Record<string, number> = {
  "4inch": 0.44,
  "6inch": 1.0,
  "8inch": 1.78,
};

const SIZE_LABELS: Record<string, string> = {
  "4inch": "4-inch",
  "6inch": "6-inch",
  "8inch": "8-inch",
};

const AVAILABLE_SIZES: CakeSize[] = ["4inch", "6inch", "8inch"];

export default function ScalingCalculator({
  recipe,
  onScaledAmounts,
  filterSizes,
}: ScalingCalculatorProps) {
  const recipeSize = recipe.size;
  const canMultiSize = recipeSize !== "universal";

  // Determine initial checked sizes from filterSizes or recipe defaults
  const [checkedSizes, setCheckedSizes] = useState<Set<CakeSize>>(() => {
    if (!canMultiSize) return new Set();
    if (filterSizes && filterSizes.length > 1) {
      return new Set(filterSizes.filter((s) => s in SIZE_RATIOS));
    }
    if (recipe.cake_type === "chiffon") {
      return new Set([recipeSize]);
    }
    return new Set();
  });

  // Sync checkedSizes when filterSizes changes externally
  useEffect(() => {
    if (!canMultiSize) return;
    if (filterSizes && filterSizes.length > 1) {
      setCheckedSizes(new Set(filterSizes.filter((s) => s in SIZE_RATIOS)));
    }
  }, [filterSizes, canMultiSize]);

  // Anchor-based custom scaling
  const [anchorId, setAnchorId] = useState<number | null>(null);
  const [targetAmount, setTargetAmount] = useState<string>("");

  // Compute scaled amounts from multi-size checkboxes
  const multiSizeAmounts = useMemo(() => {
    if (!canMultiSize || checkedSizes.size === 0) return null;

    const sourceRatio = SIZE_RATIOS[recipeSize] ?? 1.0;
    const amounts: Record<number, number> = {};

    for (const ing of recipe.ingredients) {
      let total = 0;
      for (const size of checkedSizes) {
        const targetRatio = SIZE_RATIOS[size] ?? 1.0;
        const factor = targetRatio / sourceRatio;
        total += ing.is_scalable
          ? Math.round(ing.amount * factor * 10) / 10
          : ing.amount;
      }
      // For non-scalable ingredients checked multiple times, don't multiply
      if (!ing.is_scalable && checkedSizes.size > 1) {
        total = ing.amount;
      }
      amounts[ing.id] = Math.round(total * 10) / 10;
    }
    return amounts;
  }, [canMultiSize, checkedSizes, recipe, recipeSize]);

  // Compute anchor-based scaled amounts
  const anchorAmounts = useMemo(() => {
    if (!anchorId || !targetAmount) return null;
    const anchor = recipe.ingredients.find((i) => i.id === anchorId);
    if (!anchor || anchor.amount === 0) return null;

    const parsedTarget = parseFloat(targetAmount);
    if (isNaN(parsedTarget) || parsedTarget <= 0) return null;

    const factor = parsedTarget / anchor.amount;
    const amounts: Record<number, number> = {};
    for (const ing of recipe.ingredients) {
      amounts[ing.id] = ing.is_scalable
        ? Math.round(ing.amount * factor * 10) / 10
        : ing.amount;
    }
    return amounts;
  }, [anchorId, targetAmount, recipe.ingredients]);

  // Determine which amounts to use and propagate
  const activeAmounts = anchorAmounts ?? multiSizeAmounts ?? null;

  // Propagate to parent when amounts change
  useEffect(() => {
    onScaledAmounts(activeAmounts ?? {});
  }, [activeAmounts, onScaledAmounts]);

  const handleSizeToggle = (size: CakeSize) => {
    setCheckedSizes((prev) => {
      const next = new Set(prev);
      if (next.has(size)) {
        next.delete(size);
      } else {
        next.add(size);
      }
      return next;
    });
    // Clear anchor scaling when using size checkboxes
    setAnchorId(null);
    setTargetAmount("");
  };

  const handleAnchorSelect = (ing: BakingIngredient) => {
    setAnchorId(ing.id);
    setTargetAmount(String(ing.amount));
  };

  const scalableIngredients = recipe.ingredients.filter((i) => i.is_scalable);

  return (
    <div className="space-y-4">
      {/* Multi-size checkboxes (all scalable recipe types) */}
      {canMultiSize && (
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Size Selection
          </h4>
          <p className="text-xs text-gray-400 mb-2">
            Check multiple sizes to sum ingredients
          </p>
          <div className="flex gap-2">
            {AVAILABLE_SIZES.map((size) => (
              <label
                key={size}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border cursor-pointer
                  transition-colors text-sm font-medium
                  ${
                    checkedSizes.has(size)
                      ? "bg-amber-100 border-amber-400 text-amber-800"
                      : "bg-white border-gray-200 text-gray-600 hover:border-amber-200"
                  }`}
              >
                <input
                  type="checkbox"
                  checked={checkedSizes.has(size)}
                  onChange={() => handleSizeToggle(size)}
                  className="accent-amber-600 w-3.5 h-3.5"
                />
                {SIZE_LABELS[size]}
              </label>
            ))}
          </div>
          {checkedSizes.size > 1 && (
            <p className="text-xs text-amber-600 mt-1.5 font-medium">
              Summing {[...checkedSizes].map((s) => SIZE_LABELS[s]).join(" + ")}
            </p>
          )}
        </div>
      )}

      {/* Anchor-based scaling */}
      <div>
        <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
          Scale by Ingredient
        </h4>
        <div className="flex gap-2 items-end">
          <div className="flex-1">
            <label className="block text-xs text-gray-400 mb-1">
              Anchor ingredient
            </label>
            <select
              value={anchorId ?? ""}
              onChange={(e) => {
                const id = Number(e.target.value);
                if (id > 0) {
                  const ing = scalableIngredients.find((i) => i.id === id);
                  if (ing) handleAnchorSelect(ing);
                } else {
                  setAnchorId(null);
                  setTargetAmount("");
                }
              }}
              className="w-full text-sm border border-gray-200 rounded-lg px-2 py-1.5
                         focus:outline-none focus:ring-2 focus:ring-amber-400"
            >
              <option value="">-- select --</option>
              {scalableIngredients.map((ing) => (
                <option key={ing.id} value={ing.id}>
                  {ing.name_zh ?? ing.name} ({ing.amount}
                  {ing.unit})
                </option>
              ))}
            </select>
          </div>
          <div className="w-24">
            <label className="block text-xs text-gray-400 mb-1">
              Target amount
            </label>
            <input
              type="number"
              min="0"
              step="0.1"
              value={targetAmount}
              onChange={(e) => setTargetAmount(e.target.value)}
              disabled={!anchorId}
              className="w-full text-sm border border-gray-200 rounded-lg px-2 py-1.5
                         font-mono focus:outline-none focus:ring-2 focus:ring-amber-400
                         disabled:opacity-40"
            />
          </div>
        </div>
        {anchorAmounts && (
          <p className="text-xs text-amber-600 mt-1 font-medium">
            Scale factor:{" "}
            {(parseFloat(targetAmount) /
              (recipe.ingredients.find((i) => i.id === anchorId)?.amount ?? 1)
            ).toFixed(2)}
            x
          </p>
        )}
      </div>

      {/* Reset */}
      {activeAmounts && (
        <button
          onClick={() => {
            if (canMultiSize) {
              // If filter has multiple sizes, reset to those
              if (filterSizes && filterSizes.length > 1) {
                setCheckedSizes(
                  new Set(filterSizes.filter((s) => s in SIZE_RATIOS))
                );
              } else if (recipe.cake_type === "chiffon") {
                setCheckedSizes(new Set([recipeSize]));
              } else {
                setCheckedSizes(new Set());
              }
            } else {
              setCheckedSizes(new Set());
            }
            setAnchorId(null);
            setTargetAmount("");
          }}
          className="text-xs text-gray-400 hover:text-amber-600 underline transition-colors"
        >
          Reset to original
        </button>
      )}
    </div>
  );
}
