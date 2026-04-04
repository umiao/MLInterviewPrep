"""Pydantic schemas for Baking Studio endpoints."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IngredientBase(BaseModel):
    """Base schema for a baking ingredient."""

    name: str
    name_zh: str | None = None
    amount: float
    unit: str
    group_name: str = "main"
    sort_order: int = 0
    is_scalable: bool = True


class RecipeCreate(BaseModel):
    """Schema for creating a new baking recipe."""

    name: str
    name_zh: str | None = None
    cake_type: str
    category: str
    size: str = "6inch"
    format: str = "full"
    steps: list[str] | None = None
    notes: str | None = None
    ingredients: list[IngredientBase] = []


class RecipeUpdate(BaseModel):
    """Schema for partial update of a baking recipe."""

    name: str | None = None
    name_zh: str | None = None
    cake_type: str | None = None
    category: str | None = None
    size: str | None = None
    format: str | None = None
    steps: list[str] | None = None
    notes: str | None = None


class IngredientResponse(IngredientBase):
    """Response schema for a baking ingredient."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    recipe_id: int


class RecipeResponse(BaseModel):
    """Response schema for a baking recipe with ingredients."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    name_zh: str | None
    cake_type: str
    category: str
    size: str
    format: str
    steps: list[str] | None
    notes: str | None
    is_preset: bool
    ingredients: list[IngredientResponse]
    created_at: datetime
    updated_at: datetime


class ScaleRequest(BaseModel):
    """Request to scale recipe ingredients by anchoring one ingredient."""

    anchor_ingredient_id: int
    target_amount: float


class ScaleResponse(BaseModel):
    """Response with scaled ingredient amounts."""

    recipe_id: int
    scale_factor: float
    ingredients: list[IngredientResponse]


class HomeInventoryItem(BaseModel):
    """Schema for a home inventory item."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    name_zh: str | None
    category: str
    in_stock: bool
    amount: float | None = None
    unit: str | None = None
    notes: str | None


class HomeInventoryCreate(BaseModel):
    """Schema for creating/updating a home inventory item."""

    name: str
    name_zh: str | None = None
    category: str = "decoration"
    in_stock: bool = True
    amount: float | None = None
    unit: str | None = None
    notes: str | None = None
