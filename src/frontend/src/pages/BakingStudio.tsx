import { useState } from "react";
import { useRecipes, useDeleteRecipe } from "../hooks/useBaking";
import type { RecipeFilters } from "../types/baking";
import FilterBar from "../components/baking/FilterBar";
import RecipeCard from "../components/baking/RecipeCard";
import RecipeDetail from "../components/baking/RecipeDetail";
import RecipeCombiner from "../components/baking/RecipeCombiner";
import LoadingSpinner from "../components/ui/LoadingSpinner";

type ViewMode = "browse" | "build";

export default function BakingStudio() {
  const [mode, setMode] = useState<ViewMode>("browse");
  const [filters, setFilters] = useState<RecipeFilters>({});
  const [selectedRecipeId, setSelectedRecipeId] = useState<number | null>(null);
  const { data: recipes, isLoading, error } = useRecipes(filters);
  const deleteRecipe = useDeleteRecipe();

  const selectedRecipe = recipes?.find((r) => r.id === selectedRecipeId) ?? null;

  const handleDelete = (id: number) => {
    deleteRecipe.mutate(id, {
      onSuccess: () => setSelectedRecipeId(null),
    });
  };

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

      {/* Mode toggle */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit">
        <button
          type="button"
          onClick={() => setMode("browse")}
          className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
            mode === "browse"
              ? "bg-white text-amber-700 shadow-sm"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Browse Recipes
        </button>
        <button
          type="button"
          onClick={() => setMode("build")}
          className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
            mode === "build"
              ? "bg-white text-amber-700 shadow-sm"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Build Your Own
        </button>
      </div>

      {/* Build mode */}
      {mode === "build" && <RecipeCombiner />}

      {/* Browse mode */}
      {mode === "browse" && (
        <>
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
        <div className="flex gap-6">
          {/* Recipe grid */}
          <div
            className={`grid grid-cols-1 gap-4 ${
              selectedRecipe
                ? "md:grid-cols-1 lg:grid-cols-2 flex-1 min-w-0"
                : "md:grid-cols-2 lg:grid-cols-3 w-full"
            }`}
          >
            {recipes.map((recipe) => (
              <RecipeCard
                key={recipe.id}
                recipe={recipe}
                onClick={() =>
                  setSelectedRecipeId(
                    recipe.id === selectedRecipeId ? null : recipe.id
                  )
                }
              />
            ))}
          </div>

          {/* Detail panel */}
          {selectedRecipe && (
            <div className="hidden md:block w-96 shrink-0 sticky top-4 self-start">
              <RecipeDetail
                recipe={selectedRecipe}
                onClose={() => setSelectedRecipeId(null)}
                onDelete={handleDelete}
              />
            </div>
          )}
        </div>
      )}

      {/* Mobile detail overlay */}
      {selectedRecipe && (
        <div className="md:hidden fixed inset-0 z-50 bg-black/40 flex items-end">
          <div className="w-full max-h-[85vh] overflow-y-auto rounded-t-2xl">
            <RecipeDetail
              recipe={selectedRecipe}
              onClose={() => setSelectedRecipeId(null)}
              onDelete={handleDelete}
            />
          </div>
        </div>
      )}
        </>
      )}
    </div>
  );
}
