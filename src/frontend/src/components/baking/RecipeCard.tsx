import type { BakingRecipe, CakeCategory } from "../../types/baking";

interface RecipeCardProps {
  recipe: BakingRecipe;
  onClick: () => void;
}

const CATEGORY_LABELS: Record<CakeCategory, string> = {
  complete: "Complete",
  base: "Base",
  cream: "Cream",
  decoration: "Decoration",
};

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

const CATEGORY_PILL: Record<CakeCategory, string> = {
  complete: "bg-amber-200/60 text-amber-900",
  base: "bg-emerald-200/60 text-emerald-900",
  cream: "bg-pink-200/60 text-pink-900",
  decoration: "bg-violet-200/60 text-violet-900",
};

export default function RecipeCard({ recipe, onClick }: RecipeCardProps) {
  const theme = CAKE_TYPE_THEMES[recipe.cake_type] ?? DEFAULT_THEME;

  return (
    <button
      onClick={onClick}
      className={`w-full text-left rounded-xl border-2 shadow-md p-4
                  transition-all hover:scale-[1.02] hover:shadow-lg focus:outline-none
                  focus:ring-2 focus:ring-offset-1 focus:ring-amber-400
                  ${theme.card}`}
    >
      {/* Top: cake type badge */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <span
          className={`px-2.5 py-1 rounded-lg text-xs font-bold tracking-wide uppercase ${theme.badge}`}
        >
          {CAKE_TYPE_LABELS[recipe.cake_type] ?? recipe.cake_type}
        </span>
        <span
          className={`px-2 py-0.5 rounded-full text-[11px] font-medium ${CATEGORY_PILL[recipe.category]}`}
        >
          {CATEGORY_LABELS[recipe.category]}
        </span>
      </div>

      {/* Name */}
      <h3 className={`font-bold text-base leading-tight mb-0.5 ${theme.accent}`}>
        {recipe.name}
      </h3>

      {/* Chinese name */}
      {recipe.name_zh && (
        <p className="text-sm text-gray-500 mb-2">{recipe.name_zh}</p>
      )}

      {/* Footer: size + ingredient count */}
      <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
        <div className="flex items-center gap-1.5">
          <span className={`inline-flex items-center justify-center w-5 h-5 rounded-full text-[10px] font-bold ${theme.iconBg}`}>
            {recipe.size === "universal" ? "U" : recipe.size.replace("inch", "\"")}
          </span>
          <span className="font-medium">{recipe.size === "universal" ? "Universal" : recipe.size.replace("inch", "-inch")}</span>
        </div>
        <span className="font-medium">{recipe.ingredients.length} ingredients</span>
      </div>
    </button>
  );
}
