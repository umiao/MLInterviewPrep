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

  return (
    <button
      onClick={onClick}
      className={`w-full text-left rounded-lg border shadow-sm px-3 py-2
                  transition-all hover:shadow-md focus:outline-none
                  focus:ring-2 focus:ring-offset-1 focus:ring-amber-400
                  ${theme.card}`}
    >
      {/* Top row: name + cake type badge */}
      <div className="flex items-center justify-between gap-2">
        <div className="min-w-0 flex-1">
          <h3 className={`font-bold text-sm leading-tight truncate ${theme.accent}`}>
            {recipe.name}
          </h3>
          {recipe.name_zh && (
            <p className="text-xs font-medium text-gray-500 truncate">{recipe.name_zh}</p>
          )}
        </div>
        <span
          className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wide uppercase shrink-0 ${theme.badge}`}
        >
          {CAKE_TYPE_LABELS[recipe.cake_type] ?? recipe.cake_type}
        </span>
      </div>

      {/* Footer: size + ingredient count */}
      <div className="flex items-center justify-between mt-1.5 text-[11px] text-gray-400">
        <div className="flex items-center gap-1">
          <span className={`inline-flex items-center justify-center w-4 h-4 rounded-full text-[9px] font-bold ${theme.iconBg}`}>
            {recipe.size === "universal" ? "U" : recipe.size.replace("inch", "\"")}
          </span>
          <span>{recipe.size === "universal" ? "Universal" : recipe.size.replace("inch", "-inch")}</span>
        </div>
        <span>{recipe.ingredients.length} ingr.</span>
      </div>
    </button>
  );
}
