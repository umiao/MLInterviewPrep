import type { BakingRecipe } from "../../types/baking";

interface RecipeCardProps {
  recipe: BakingRecipe;
  onClick: () => void;
}

const CAKE_TYPE_LABELS: Record<string, string> = {
  basque: "Basque",
  cheesecake: "Cheesecake",
  chiffon: "Chiffon",
  cream_cake: "Cream",
};

/**
 * Per-cake-type color themes: border, background gradient, badge bg, badge text, accent
 */
const CAKE_TYPE_THEMES: Record<
  string,
  {
    card: string;
    badge: string;
    accent: string;
    iconBg: string;
  }
> = {
  basque: {
    card: "border-amber-300 bg-gradient-to-br from-amber-50 to-orange-50",
    badge: "bg-amber-500 text-white",
    accent: "text-amber-700",
    iconBg: "bg-amber-100 text-amber-600",
  },
  cheesecake: {
    card: "border-yellow-300 bg-gradient-to-br from-yellow-50 to-amber-50",
    badge: "bg-yellow-500 text-white",
    accent: "text-yellow-700",
    iconBg: "bg-yellow-100 text-yellow-600",
  },
  chiffon: {
    card: "border-emerald-300 bg-gradient-to-br from-emerald-50 to-teal-50",
    badge: "bg-emerald-500 text-white",
    accent: "text-emerald-700",
    iconBg: "bg-emerald-100 text-emerald-600",
  },
  cream_cake: {
    card: "border-pink-300 bg-gradient-to-br from-pink-50 to-rose-50",
    badge: "bg-pink-500 text-white",
    accent: "text-pink-700",
    iconBg: "bg-pink-100 text-pink-600",
  },
};

const DEFAULT_THEME = {
  card: "border-gray-200 bg-white",
  badge: "bg-gray-500 text-white",
  accent: "text-gray-700",
  iconBg: "bg-gray-100 text-gray-600",
};

export default function RecipeCard({ recipe, onClick }: RecipeCardProps) {
  const theme = CAKE_TYPE_THEMES[recipe.cake_type] ?? DEFAULT_THEME;
  const sizeLabel = recipe.size === "universal" ? "U" : recipe.size.replace("inch", "\"");

  return (
    <button
      onClick={onClick}
      className={`w-full text-left rounded-md border px-2.5 py-1.5
                  transition-all hover:shadow-sm focus:outline-none
                  focus:ring-1 focus:ring-amber-400
                  ${theme.card}`}
    >
      <div className="flex items-center gap-2">
        {/* Size badge */}
        <span className={`inline-flex items-center justify-center w-6 h-6 rounded text-[10px] font-bold shrink-0 ${theme.iconBg}`}>
          {sizeLabel}
        </span>

        {/* Name + Chinese name */}
        <div className="min-w-0 flex-1">
          <span className={`font-bold text-sm leading-none ${theme.accent}`}>
            {recipe.name}
          </span>
          {recipe.name_zh && (
            <span className="text-xs text-gray-400 ml-1.5">{recipe.name_zh}</span>
          )}
        </div>

        {/* Ingredient count + type badge */}
        <span className="text-[10px] text-gray-400 shrink-0">{recipe.ingredients.length}</span>
        <span
          className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase shrink-0 ${theme.badge}`}
        >
          {CAKE_TYPE_LABELS[recipe.cake_type] ?? recipe.cake_type}
        </span>
      </div>
    </button>
  );
}
