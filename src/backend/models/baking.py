"""SQLAlchemy models for Baking Studio module."""
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from src.backend.database import Base


class BakingRecipe(Base):
    """A baking recipe with metadata and scaling info."""

    __tablename__ = "baking_recipes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    name_zh = Column(String, nullable=True)
    cake_type = Column(String, nullable=False)  # basque | cheesecake | chiffon | cream_cake
    category = Column(String, nullable=False)  # base | cream | decoration | complete
    size = Column(String, default="6inch")  # 4inch | 6inch | universal
    format = Column(String, default="full")  # full | box
    steps = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    is_preset = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    ingredients = relationship(
        "BakingIngredient",
        backref="recipe",
        cascade="all, delete-orphan",
        order_by="BakingIngredient.sort_order",
    )


class BakingIngredient(Base):
    """An ingredient line within a baking recipe."""

    __tablename__ = "baking_ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(
        Integer,
        ForeignKey("baking_recipes.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String, nullable=False)
    name_zh = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # g | ml | pc | tsp | tbsp
    group_name = Column(String, default="main")  # main | topping | frosting | filling
    sort_order = Column(Integer, default=0)
    is_scalable = Column(Boolean, default=True)


class HomeInventory(Base):
    """Tracks baking supplies available at home."""

    __tablename__ = "baking_home_inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    name_zh = Column(String, nullable=True)
    category = Column(String, default="decoration")  # decoration | staple | dairy | fruit
    in_stock = Column(Boolean, default=True)
    amount = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
