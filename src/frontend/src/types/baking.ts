export type CakeType = "basque" | "cheesecake" | "chiffon" | "cream_cake";
export type CakeCategory = "base" | "cream" | "decoration" | "complete";
export type CakeSize = "4inch" | "6inch" | "8inch" | "universal";
export type CakeFormat = "full" | "box";
export type IngredientUnit = "g" | "ml" | "pc" | "tsp" | "tbsp";

export interface BakingIngredient {
  id: number;
  recipe_id: number;
  name: string;
  name_zh: string | null;
  amount: number;
  unit: string;
  group_name: string;
  sort_order: number;
  is_scalable: boolean;
}

export interface BakingRecipe {
  id: number;
  name: string;
  name_zh: string | null;
  cake_type: CakeType;
  category: CakeCategory;
  size: CakeSize;
  format: CakeFormat;
  steps: string[] | null;
  notes: string | null;
  is_preset: boolean;
  ingredients: BakingIngredient[];
  created_at: string;
  updated_at: string;
}

export interface RecipeCreatePayload {
  name: string;
  name_zh?: string;
  cake_type: CakeType;
  category: CakeCategory;
  size?: CakeSize;
  format?: CakeFormat;
  steps?: string[];
  notes?: string;
  ingredients: Omit<BakingIngredient, "id" | "recipe_id">[];
}

export interface ScaleRequest {
  anchor_ingredient_id: number;
  target_amount: number;
}

export interface ScaleResponse {
  recipe_id: number;
  scale_factor: number;
  ingredients: BakingIngredient[];
}

export interface HomeInventoryItem {
  id: number;
  name: string;
  name_zh: string | null;
  category: string;
  in_stock: boolean;
  amount: number | null;
  unit: string | null;
  notes: string | null;
}

export interface RecipeFilters {
  cake_type?: CakeType;
  category?: CakeCategory;
  size?: CakeSize;
  format?: CakeFormat;
}
