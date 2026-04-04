import { useState } from "react";
import { useRecipes } from "../hooks/useBaking";
import type { RecipeFilters } from "../types/baking";
import FilterBar from "../components/baking/FilterBar";
import RecipeCard from "../components/baking/RecipeCard";
import LoadingSpinner from "../components/ui/LoadingSpinner";

export default function BakingStudio() {
  const [filters, setFilters] = useState<RecipeFilters>({});
  const [selectedRecipeId, setSelectedRecipeId] = useState<number | null>(null);
  const { data: recipes, isLoading, error } = useRecipes(filters);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Baking Studio</h1>
        <button
          className="px-4 py-2 rounded-lg bg-amber-600 text-white font-medium
                     hover:bg-amber-700 transition-colors shadow-sm"
        >
          + New Recipe
        </button>
      </div>

      {/* Filters */}
      <FilterBar filters={filters} onFilterChange={setFilters} />

      {/* Content */}
      {isLoading ? (
        <LoadingSpinner message="Loading recipes..." fullHeight />
      ) : error ? (
        <div className="text-center py-12 text-red-500">
          Failed to load recipes. Please try again.
        </div>
      ) : !recipes || recipes.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <p className="text-lg font-medium mb-1">No recipes found</p>
          <p className="text-sm">Create your first recipe!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recipes.map((recipe) => (
            <RecipeCard
              key={recipe.id}
              recipe={recipe}
              onClick={() => setSelectedRecipeId(recipe.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
