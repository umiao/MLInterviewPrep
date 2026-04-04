import { useState, useMemo } from "react";
import { useRecipes, useInventory, useCreateRecipe } from "../../hooks/useBaking";
import type {
  BakingRecipe,
  HomeInventoryItem,
  RecipeCreatePayload,
} from "../../types/baking";
import StepIndicator from "./StepIndicator";

/* ------------------------------------------------------------------ */
/*  Merge types & logic                                                */
/* ------------------------------------------------------------------ */

interface MergedIngredient {
  name: string;
  name_zh: string | null;
  amount: number;
  unit: string;
  source: string;
  group_name: string;
  is_scalable: boolean;
}

function mergeIngredients(
  selections: { recipe: BakingRecipe; scaledAmounts?: Record<number, number> }[],
  decorations: HomeInventoryItem[]
): MergedIngredient[] {
  const result: MergedIngredient[] = [];

  for (const { recipe, scaledAmounts } of selections) {
    for (const ing of recipe.ingredients) {
      const amount = scaledAmounts?.[ing.id] ?? ing.amount;
      // Same name + unit from same recipe source -> sum amounts
      const existing = result.find(
        (r) => r.name === ing.name && r.unit === ing.unit && r.source === recipe.name
      );
      if (existing) {
        existing.amount += amount;
        existing.amount = Math.round(existing.amount * 10) / 10;
      } else {
        result.push({
          name: ing.name,
          name_zh: ing.name_zh,
          amount: Math.round(amount * 10) / 10,
          unit: ing.unit,
          source: recipe.name,
          group_name: recipe.name + ": " + ing.group_name,
          is_scalable: ing.is_scalable,
        });
      }
    }
  }

  // Decorations as separate "to taste" items — never merged with recipe ingredients
  for (const dec of decorations) {
    result.push({
      name: dec.name,
      name_zh: dec.name_zh,
      amount: 0,
      unit: "to taste",
      source: "Decorations",
      group_name: "Decorations",
      is_scalable: false,
    });
  }

  return result;
}

/* ------------------------------------------------------------------ */
/*  Sub-components                                                     */
/* ------------------------------------------------------------------ */

function SelectableCard({
  label,
  sublabel,
  selected,
  onClick,
}: {
  label: string;
  sublabel?: string | null;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`text-left p-3 rounded-lg border-2 transition-all ${
        selected
          ? "border-amber-500 bg-amber-50 shadow-sm"
          : "border-gray-200 bg-white hover:border-amber-300"
      }`}
    >
      <p className="text-sm font-medium text-gray-900">{label}</p>
      {sublabel && <p className="text-xs text-gray-500 mt-0.5">{sublabel}</p>}
    </button>
  );
}

function ToggleChip({
  label,
  sublabel,
  selected,
  onClick,
}: {
  label: string;
  sublabel?: string | null;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-3 py-1.5 rounded-full text-sm transition-all ${
        selected
          ? "bg-amber-500 text-white"
          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
      }`}
    >
      {sublabel ? `${sublabel} (${label})` : label}
    </button>
  );
}

/* ------------------------------------------------------------------ */
/*  Preview panel                                                      */
/* ------------------------------------------------------------------ */

function PreviewPanel({ merged }: { merged: MergedIngredient[] }) {
  // Group by group_name
  const groups = useMemo(() => {
    const map = new Map<string, MergedIngredient[]>();
    for (const item of merged) {
      const list = map.get(item.group_name) ?? [];
      list.push(item);
      map.set(item.group_name, list);
    }
    return Array.from(map.entries());
  }, [merged]);

  if (merged.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400 text-sm">
        Select recipes to see merged ingredients
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-gray-700">
        Merged Ingredients ({merged.length})
      </h3>
      {groups.map(([groupName, items]) => (
        <div key={groupName}>
          <p className="text-xs font-medium text-gray-500 mb-1">{groupName}</p>
          <div className="space-y-0.5">
            {items.map((item, i) => (
              <div
                key={`${item.name}-${item.unit}-${i}`}
                className="flex justify-between text-sm py-0.5"
              >
                <span className="text-gray-700">
                  {item.name_zh ? `${item.name_zh} (${item.name})` : item.name}
                </span>
                <span className="text-gray-500 tabular-nums ml-2 shrink-0">
                  {item.unit === "to taste" ? "to taste" : `${item.amount} ${item.unit}`}
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main component                                                     */
/* ------------------------------------------------------------------ */

const STEPS = ["Base", "Cream", "Decorations"];

export default function RecipeCombiner() {
  const [step, setStep] = useState(1);
  const [selectedBase, setSelectedBase] = useState<BakingRecipe | null>(null);
  const [selectedCreams, setSelectedCreams] = useState<BakingRecipe[]>([]);
  const [selectedDecorations, setSelectedDecorations] = useState<HomeInventoryItem[]>([]);
  const [saveName, setSaveName] = useState("");
  const [showSaveModal, setShowSaveModal] = useState(false);

  // Fetch data
  const { data: baseRecipes } = useRecipes({ category: "base" });
  const { data: completeRecipes } = useRecipes({ category: "complete" });
  const { data: creamRecipes } = useRecipes({ category: "cream" });
  const { data: inventory } = useInventory();
  const createRecipe = useCreateRecipe();

  // Combine base + complete for step 1
  const baseOptions = useMemo(
    () => [...(baseRecipes ?? []), ...(completeRecipes ?? [])],
    [baseRecipes, completeRecipes]
  );

  const inStockItems = useMemo(
    () => (inventory ?? []).filter((item) => item.in_stock),
    [inventory]
  );

  // Build merged list from all selections
  const merged = useMemo(() => {
    const selections: { recipe: BakingRecipe }[] = [];
    if (selectedBase) selections.push({ recipe: selectedBase });
    for (const cream of selectedCreams) selections.push({ recipe: cream });
    return mergeIngredients(selections, selectedDecorations);
  }, [selectedBase, selectedCreams, selectedDecorations]);

  // Cream multi-select toggle
  const toggleCream = (recipe: BakingRecipe) => {
    setSelectedCreams((prev) =>
      prev.some((r) => r.id === recipe.id)
        ? prev.filter((r) => r.id !== recipe.id)
        : [...prev, recipe]
    );
  };

  // Decoration toggle
  const toggleDecoration = (item: HomeInventoryItem) => {
    setSelectedDecorations((prev) =>
      prev.some((d) => d.id === item.id)
        ? prev.filter((d) => d.id !== item.id)
        : [...prev, item]
    );
  };

  // Save as custom recipe
  const handleSave = () => {
    if (!saveName.trim()) return;

    const ingredients = merged.map((m, i) => ({
      name: m.name,
      name_zh: m.name_zh,
      amount: m.amount,
      unit: m.unit,
      group_name: m.group_name,
      sort_order: i,
      is_scalable: m.is_scalable,
    }));

    // Concatenate steps from selected recipes
    const allSteps: string[] = [];
    if (selectedBase?.steps) allSteps.push(...selectedBase.steps);
    for (const cream of selectedCreams) {
      if (cream.steps) allSteps.push(...cream.steps);
    }

    const payload: RecipeCreatePayload = {
      name: saveName.trim(),
      cake_type: selectedBase?.cake_type ?? "cream_cake",
      category: "complete",
      size: selectedBase?.size,
      format: selectedBase?.format,
      steps: allSteps.length > 0 ? allSteps : undefined,
      ingredients,
    };

    createRecipe.mutate(payload, {
      onSuccess: () => {
        setShowSaveModal(false);
        setSaveName("");
      },
    });
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* Left: wizard */}
      <div className="flex-1 min-w-0 space-y-6">
        <StepIndicator steps={STEPS} currentStep={step} />

        {/* Step 1: Base */}
        {step === 1 && (
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-800">Choose a Base</h2>
            <p className="text-sm text-gray-500">
              Select a base or complete recipe, or skip this step.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <SelectableCard
                label="No base"
                sublabel="Skip this step"
                selected={selectedBase === null}
                onClick={() => setSelectedBase(null)}
              />
              {baseOptions.map((recipe) => (
                <SelectableCard
                  key={recipe.id}
                  label={recipe.name}
                  sublabel={recipe.name_zh}
                  selected={selectedBase?.id === recipe.id}
                  onClick={() =>
                    setSelectedBase(selectedBase?.id === recipe.id ? null : recipe)
                  }
                />
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Cream/Filling */}
        {step === 2 && (
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-800">Choose Cream / Filling</h2>
            <p className="text-sm text-gray-500">
              Select one or more creams, or skip.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {(!creamRecipes || creamRecipes.length === 0) ? (
                <p className="text-sm text-gray-400 col-span-2">No cream recipes available.</p>
              ) : (
                creamRecipes.map((recipe) => (
                  <SelectableCard
                    key={recipe.id}
                    label={recipe.name}
                    sublabel={recipe.name_zh}
                    selected={selectedCreams.some((r) => r.id === recipe.id)}
                    onClick={() => toggleCream(recipe)}
                  />
                ))
              )}
            </div>
          </div>
        )}

        {/* Step 3: Decorations */}
        {step === 3 && (
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-800">Choose Decorations</h2>
            <p className="text-sm text-gray-500">
              Toggle items from your home inventory.
            </p>
            <div className="flex flex-wrap gap-2">
              {inStockItems.length === 0 ? (
                <p className="text-sm text-gray-400">No in-stock inventory items.</p>
              ) : (
                inStockItems.map((item) => (
                  <ToggleChip
                    key={item.id}
                    label={item.name}
                    sublabel={item.name_zh}
                    selected={selectedDecorations.some((d) => d.id === item.id)}
                    onClick={() => toggleDecoration(item)}
                  />
                ))
              )}
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between pt-4 border-t border-gray-100">
          <button
            type="button"
            onClick={() => setStep((s) => Math.max(1, s - 1))}
            disabled={step === 1}
            className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg
                       hover:bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Back
          </button>
          {step < 3 ? (
            <button
              type="button"
              onClick={() => setStep((s) => Math.min(3, s + 1))}
              className="px-4 py-2 text-sm font-medium text-white bg-amber-600 rounded-lg
                         hover:bg-amber-700 transition-colors"
            >
              Next
            </button>
          ) : (
            <button
              type="button"
              onClick={() => setShowSaveModal(true)}
              disabled={merged.length === 0}
              className="px-4 py-2 text-sm font-medium text-white bg-emerald-600 rounded-lg
                         hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Save as Custom Recipe
            </button>
          )}
        </div>
      </div>

      {/* Right: preview panel */}
      <div className="lg:w-80 shrink-0">
        <div className="bg-white rounded-xl border border-amber-100 shadow-sm p-4 sticky top-4">
          <PreviewPanel merged={merged} />
        </div>
      </div>

      {/* Save modal */}
      {showSaveModal && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-sm mx-4 space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Save Custom Recipe</h3>
            <input
              type="text"
              value={saveName}
              onChange={(e) => setSaveName(e.target.value)}
              placeholder="Recipe name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                         focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent"
              autoFocus
            />
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => {
                  setShowSaveModal(false);
                  setSaveName("");
                }}
                className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSave}
                disabled={!saveName.trim() || createRecipe.isPending}
                className="px-4 py-2 text-sm font-medium text-white bg-amber-600 rounded-lg
                           hover:bg-amber-700 disabled:opacity-40 transition-colors"
              >
                {createRecipe.isPending ? "Saving..." : "Save"}
              </button>
            </div>
            {createRecipe.isError && (
              <p className="text-xs text-red-500">Failed to save. Please try again.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
