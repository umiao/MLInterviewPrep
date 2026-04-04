import type { BakingRecipe, CakeCategory } from "../../types/baking";

interface RecipeCardProps {
  recipe: BakingRecipe;
  onClick: () => void;
}

const CATEGORY_STYLES: Record<CakeCategory, string> = {
  complete: "bg-amber-100 text-amber-800",
  base: "bg-emerald-100 text-emerald-800",
  cream: "bg-pink-100 text-pink-800",
  decoration: "bg-violet-100 text-violet-800",
};

const CAKE_TYPE_LABELS: Record<string, string> = {
  basque: "Basque",
  cheesecake: "Cheesecake",
  chiffon: "Chiffon",
  cream_cake: "Cream Cake",
};

export default function RecipeCard({ recipe, onClick }: RecipeCardProps) {
  return (
    <button
      onClick={onClick}
      className="w-full text-left rounded-xl bg-white border border-amber-100 shadow-md
                 p-4 transition-all hover:scale-[1.02] hover:shadow-lg focus:outline-none
                 focus:ring-2 focus:ring-amber-400"
    >
      {/* Header: name + category badge */}
      <div className="flex items-start justify-between gap-2 mb-1">
        <h3 className="font-semibold text-gray-900 leading-tight">{recipe.name}</h3>
        <span
          className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-medium ${
            CATEGORY_STYLES[recipe.category]
          }`}
        >
          {recipe.category}
        </span>
      </div>

      {/* Chinese name */}
      {recipe.name_zh && (
        <p className="text-sm text-gray-500 mb-2">{recipe.name_zh}</p>
      )}

      {/* Footer: cake type + ingredient count */}
      <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
        <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-700 font-medium">
          {CAKE_TYPE_LABELS[recipe.cake_type] ?? recipe.cake_type}
        </span>
        <span>{recipe.ingredients.length} items</span>
      </div>
    </button>
  );
}
