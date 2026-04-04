"""Baking Studio API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from src.backend.database import get_db
from src.backend.models.baking import BakingIngredient, BakingRecipe, HomeInventory
from src.backend.schemas.baking import (
    HomeInventoryCreate,
    HomeInventoryItem,
    IngredientBase,
    IngredientResponse,
    RecipeCreate,
    RecipeResponse,
    RecipeUpdate,
    ScaleRequest,
    ScaleResponse,
)

router = APIRouter()

SIZE_RATIOS = {"4inch": 0.44, "6inch": 1.0, "8inch": 1.78}


@router.get("/baking/recipes", response_model=list[RecipeResponse])
def list_recipes(
    cake_type: str | None = Query(default=None),
    category: str | None = Query(default=None),
    size: str | None = Query(default=None),
    format: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[BakingRecipe]:
    """List all baking recipes with optional filters.

    Args:
        cake_type: Filter by cake type (basque, cheesecake, chiffon, cream_cake).
        category: Filter by category (base, cream, decoration, complete).
        size: Filter by size (4inch, 6inch, 8inch, universal).
        format: Filter by format (full, box).
        db: Database session.

    Returns:
        List of baking recipes with ingredients.
    """
    query = (
        db.query(BakingRecipe)
        .options(joinedload(BakingRecipe.ingredients))
    )
    if cake_type:
        query = query.filter(BakingRecipe.cake_type == cake_type)
    if category:
        query = query.filter(BakingRecipe.category == category)
    if size:
        query = query.filter(BakingRecipe.size == size)
    if format:
        query = query.filter(BakingRecipe.format == format)
    return query.all()


@router.get("/baking/recipes/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
) -> BakingRecipe:
    """Get a single baking recipe with its ingredients.

    Args:
        recipe_id: ID of the recipe.
        db: Database session.

    Returns:
        The baking recipe.
    """
    recipe = (
        db.query(BakingRecipe)
        .options(joinedload(BakingRecipe.ingredients))
        .filter(BakingRecipe.id == recipe_id)
        .first()
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("/baking/recipes", response_model=RecipeResponse, status_code=201)
def create_recipe(
    data: RecipeCreate,
    db: Session = Depends(get_db),
) -> BakingRecipe:
    """Create a new baking recipe with ingredients.

    Args:
        data: Recipe creation data including ingredients.
        db: Database session.

    Returns:
        Created recipe with ingredients.
    """
    recipe = BakingRecipe(
        name=data.name,
        name_zh=data.name_zh,
        cake_type=data.cake_type,
        category=data.category,
        size=data.size,
        format=data.format,
        steps=data.steps,
        notes=data.notes,
        is_preset=False,
    )
    db.add(recipe)
    db.flush()

    for ing_data in data.ingredients:
        ingredient = BakingIngredient(
            recipe_id=recipe.id,
            name=ing_data.name,
            name_zh=ing_data.name_zh,
            amount=ing_data.amount,
            unit=ing_data.unit,
            group_name=ing_data.group_name,
            sort_order=ing_data.sort_order,
            is_scalable=ing_data.is_scalable,
        )
        db.add(ingredient)

    db.commit()
    db.refresh(recipe)
    return recipe


@router.put("/baking/recipes/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    data: RecipeUpdate,
    db: Session = Depends(get_db),
) -> BakingRecipe:
    """Update a baking recipe's metadata (partial update).

    Args:
        recipe_id: ID of the recipe to update.
        data: Partial update data.
        db: Database session.

    Returns:
        Updated recipe.
    """
    recipe = (
        db.query(BakingRecipe)
        .options(joinedload(BakingRecipe.ingredients))
        .filter(BakingRecipe.id == recipe_id)
        .first()
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(recipe, field, value)

    db.commit()
    db.refresh(recipe)
    return recipe


@router.delete("/baking/recipes/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Delete a baking recipe (CASCADE deletes ingredients).

    Args:
        recipe_id: ID of the recipe to delete.
        db: Database session.

    Returns:
        Deletion confirmation.
    """
    recipe = (
        db.query(BakingRecipe).filter(BakingRecipe.id == recipe_id).first()
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db.delete(recipe)
    db.commit()
    return {"deleted": True}


@router.post(
    "/baking/recipes/{recipe_id}/scale", response_model=ScaleResponse
)
def scale_recipe(
    recipe_id: int,
    data: ScaleRequest,
    target_size: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict:
    """Scale recipe ingredients by anchoring one ingredient to a target amount.

    Optionally apply a size ratio if target_size is provided.

    Args:
        recipe_id: ID of the recipe to scale.
        data: Scale request with anchor ingredient and target amount.
        target_size: Optional target size for ratio-based scaling.
        db: Database session.

    Returns:
        Scaled ingredients with scale factor.
    """
    recipe = (
        db.query(BakingRecipe)
        .options(joinedload(BakingRecipe.ingredients))
        .filter(BakingRecipe.id == recipe_id)
        .first()
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    anchor = (
        db.query(BakingIngredient)
        .filter(BakingIngredient.id == data.anchor_ingredient_id)
        .first()
    )
    if not anchor or anchor.recipe_id != recipe_id:
        raise HTTPException(status_code=404, detail="Anchor ingredient not found in this recipe")

    if anchor.amount == 0:
        raise HTTPException(status_code=400, detail="Anchor ingredient amount is zero")

    scale_factor = data.target_amount / anchor.amount

    # Apply size ratio if target_size is given
    if target_size:
        if target_size not in SIZE_RATIOS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown size: {target_size}. Valid: {list(SIZE_RATIOS.keys())}",
            )
        source_ratio = SIZE_RATIOS.get(recipe.size, 1.0)
        target_ratio = SIZE_RATIOS[target_size]
        scale_factor *= target_ratio / source_ratio

    scaled_ingredients = []
    for ing in recipe.ingredients:
        scaled_amount = round(ing.amount * scale_factor, 1) if ing.is_scalable else ing.amount
        scaled_ingredients.append(
            IngredientResponse(
                id=ing.id,
                recipe_id=ing.recipe_id,
                name=ing.name,
                name_zh=ing.name_zh,
                amount=scaled_amount,
                unit=ing.unit,
                group_name=ing.group_name,
                sort_order=ing.sort_order,
                is_scalable=ing.is_scalable,
            )
        )

    return {
        "recipe_id": recipe_id,
        "scale_factor": round(scale_factor, 4),
        "ingredients": scaled_ingredients,
    }


@router.get("/baking/inventory", response_model=list[HomeInventoryItem])
def list_inventory(
    db: Session = Depends(get_db),
) -> list[HomeInventory]:
    """List all home inventory items.

    Args:
        db: Database session.

    Returns:
        List of home inventory items.
    """
    return db.query(HomeInventory).order_by(HomeInventory.category, HomeInventory.name).all()


@router.post("/baking/inventory", response_model=HomeInventoryItem, status_code=201)
def upsert_inventory(
    data: HomeInventoryCreate,
    db: Session = Depends(get_db),
) -> HomeInventory:
    """Add or update a home inventory item (upsert by name).

    Args:
        data: Inventory item data.
        db: Database session.

    Returns:
        Created or updated inventory item.
    """
    existing = (
        db.query(HomeInventory).filter(HomeInventory.name == data.name).first()
    )
    if existing:
        for field, value in data.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    item = HomeInventory(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post(
    "/baking/recipes/{recipe_id}/ingredients",
    response_model=IngredientResponse,
    status_code=201,
)
def add_ingredient(
    recipe_id: int,
    data: IngredientBase,
    db: Session = Depends(get_db),
) -> BakingIngredient:
    """Add an ingredient to a recipe.

    Args:
        recipe_id: ID of the recipe.
        data: Ingredient data.
        db: Database session.

    Returns:
        Created ingredient.
    """
    recipe = (
        db.query(BakingRecipe).filter(BakingRecipe.id == recipe_id).first()
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    ingredient = BakingIngredient(
        recipe_id=recipe_id,
        name=data.name,
        name_zh=data.name_zh,
        amount=data.amount,
        unit=data.unit,
        group_name=data.group_name,
        sort_order=data.sort_order,
        is_scalable=data.is_scalable,
    )
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.delete("/baking/ingredients/{ingredient_id}")
def delete_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Remove an ingredient by ID.

    Args:
        ingredient_id: ID of the ingredient to delete.
        db: Database session.

    Returns:
        Deletion confirmation.
    """
    ingredient = (
        db.query(BakingIngredient)
        .filter(BakingIngredient.id == ingredient_id)
        .first()
    )
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    db.delete(ingredient)
    db.commit()
    return {"deleted": True}
