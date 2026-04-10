/**
 * TanStack Query hooks for the Baking Studio API.
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../utils/api";
import type {
  BakingRecipe,
  HomeInventoryItem,
  RecipeCreatePayload,
  RecipeFilters,
  ScaleRequest,
  ScaleResponse,
} from "../types/baking";

/* ------------------------------------------------------------------ */
/*  Query keys                                                         */
/* ------------------------------------------------------------------ */

export const BAKING_KEYS = {
  all: ["baking"] as const,
  recipes: ["baking", "recipes"] as const,
  recipeList: (filters: RecipeFilters) =>
    ["baking", "recipes", "list", filters] as const,
  recipe: (id: number) => ["baking", "recipes", "detail", id] as const,
  inventory: ["baking", "inventory"] as const,
} as const;

/* ------------------------------------------------------------------ */
/*  Recipe hooks                                                       */
/* ------------------------------------------------------------------ */

/** Fetch recipes with optional filters. */
export function useRecipes(filters?: RecipeFilters) {
  const params = new URLSearchParams();
  if (filters?.cake_type) params.set("cake_type", filters.cake_type);
  if (filters?.category) params.set("category", filters.category);
  // When a single size is selected, pass it to the API; when multiple are
  // selected we fetch all and filter client-side so combined views work.
  if (filters?.sizes?.length === 1) params.set("size", filters.sizes[0]);
  if (filters?.format) params.set("format", filters.format);
  const qs = params.toString();
  return useQuery<BakingRecipe[]>({
    queryKey: BAKING_KEYS.recipeList(filters ?? {}),
    queryFn: async () => {
      const recipes: BakingRecipe[] = await api.get(
        "/baking/recipes" + (qs ? "?" + qs : "")
      );
      // Client-side multi-size filter
      if (filters?.sizes && filters.sizes.length > 1) {
        const sizeSet = new Set(filters.sizes);
        return recipes.filter(
          (r) => sizeSet.has(r.size) || r.size === "universal"
        );
      }
      return recipes;
    },
  });
}

/** Fetch a single recipe by ID. */
export function useRecipe(id: number) {
  return useQuery<BakingRecipe>({
    queryKey: BAKING_KEYS.recipe(id),
    queryFn: () => api.get("/baking/recipes/" + id),
    enabled: id > 0,
  });
}

/** Create a new recipe. Invalidates all recipe lists on success. */
export function useCreateRecipe() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: RecipeCreatePayload) =>
      api.post("/baking/recipes", payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: BAKING_KEYS.recipes }),
  });
}

/** Delete a recipe. Invalidates all recipe lists on success. */
export function useDeleteRecipe() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.del("/baking/recipes/" + id),
    onSuccess: () => qc.invalidateQueries({ queryKey: BAKING_KEYS.recipes }),
  });
}

/** Scale recipe ingredients. Read-only mutation (no cache invalidation). */
export function useScaleRecipe() {
  return useMutation<ScaleResponse, Error, { recipeId: number; req: ScaleRequest }>({
    mutationFn: ({ recipeId, req }) =>
      api.post("/baking/recipes/" + recipeId + "/scale", req),
  });
}

/* ------------------------------------------------------------------ */
/*  Inventory hooks                                                    */
/* ------------------------------------------------------------------ */

/** Fetch all home inventory items. */
export function useInventory() {
  return useQuery<HomeInventoryItem[]>({
    queryKey: BAKING_KEYS.inventory,
    queryFn: () => api.get("/baking/inventory"),
  });
}
