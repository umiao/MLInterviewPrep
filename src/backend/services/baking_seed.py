"""Seed data for Baking Studio: preset recipes and home inventory."""
import logging

from sqlalchemy.orm import Session

from src.backend.models.baking import BakingIngredient, BakingRecipe, HomeInventory

logger = logging.getLogger(__name__)

SIZE_RATIOS = {"4inch": 0.44, "6inch": 1.0, "8inch": 1.78}

# (name, name_zh, category)
INVENTORY_ITEMS: list[tuple[str, str, str]] = [
    ("coconut flakes", "椰蓉", "decoration"),
    ("popping boba", "爆珠", "decoration"),
    ("fresh fruits", "水果", "decoration"),
    ("pistachios", "开心果", "decoration"),
    ("pistachio paste", "开心果酱", "staple"),
    ("cream cheese", "奶油奶酪", "dairy"),
    ("heavy cream", "淡奶油", "dairy"),
    ("eggs", "鸡蛋", "staple"),
    ("sugar", "细砂糖", "staple"),
    ("cake flour", "低筋面粉", "staple"),
    ("cornstarch", "玉米淀粉", "staple"),
    ("vegetable oil", "植物油", "staple"),
    ("milk", "牛奶", "dairy"),
    ("guava jam", "芭乐果酱", "staple"),
    ("lemon juice", "柠檬汁", "staple"),
    ("matcha powder", "抹茶粉", "staple"),
    ("cocoa powder", "可可粉", "staple"),
    ("black sesame paste", "黑芝麻酱", "staple"),
    ("sea salt", "海盐", "staple"),
    ("soy flour", "黄豆粉", "staple"),
]


def _make_ingredient(
    name: str,
    name_zh: str,
    amount: float,
    unit: str,
    group_name: str = "main",
    sort_order: int = 0,
    is_scalable: bool = True,
) -> BakingIngredient:
    """Create a BakingIngredient instance (not yet attached to a recipe)."""
    return BakingIngredient(
        name=name,
        name_zh=name_zh,
        amount=amount,
        unit=unit,
        group_name=group_name,
        sort_order=sort_order,
        is_scalable=is_scalable,
    )


def _build_preset_recipes() -> list[BakingRecipe]:
    """Build all preset recipe objects with their ingredients."""
    recipes: list[BakingRecipe] = []

    # 1. Basque Cheesecake (6-inch, complete)
    recipes.append(BakingRecipe(
        name="Pistachio Basque Cheesecake",
        name_zh="开心果巴斯克",
        cake_type="basque",
        category="complete",
        size="6inch",
        format="full",
        is_preset=True,
        steps=[
            "Mix all ingredients until smooth",
            "Chill batter 30 minutes",
            "Pour 260g into mold, add 8g lemon juice",
            "Remaining batter: mix in 55g pistachio paste",
            "Pour pistachio layer on top",
            "Bake at 450F (230C) for 23 minutes",
            "Cool to room temperature, then refrigerate 6+ hours",
        ],
        ingredients=[
            _make_ingredient("cream cheese", "奶油奶酪", 350, "g", "main", 0),
            _make_ingredient("sugar", "细砂糖", 50, "g", "main", 1),
            _make_ingredient("egg liquid", "鸡蛋液", 190, "g", "main", 2),
            _make_ingredient("egg yolk", "蛋黄", 18, "g", "main", 3),
            _make_ingredient("heavy cream", "淡奶油", 180, "g", "main", 4),
            _make_ingredient("cornstarch", "玉米淀粉", 8, "g", "main", 5),
            _make_ingredient("lemon juice", "柠檬汁", 8, "g", "filling", 6),
            _make_ingredient("pistachio paste", "开心果酱", 55, "g", "filling", 7),
        ],
    ))

    # 2. Guava Whipped Cream (universal, cream)
    recipes.append(BakingRecipe(
        name="Guava Whipped Cream",
        name_zh="芭乐奶油",
        cake_type="cream_cake",
        category="cream",
        size="universal",
        format="full",
        is_preset=True,
        steps=[
            "Chill bowl and whisk",
            "Whip heavy cream with sugar to soft peaks",
            "Fold in guava jam gently",
            "Use immediately or refrigerate up to 2 hours",
        ],
        ingredients=[
            _make_ingredient("heavy cream", "淡奶油", 250, "g", "main", 0),
            _make_ingredient("sugar", "糖", 15, "g", "main", 1),
            _make_ingredient("guava jam", "芭乐果酱", 50, "g", "main", 2),
        ],
    ))

    # 3. Basic Chiffon 4-inch (4inch, base)
    recipes.append(BakingRecipe(
        name="Basic Chiffon 4-inch",
        name_zh="基础戚风(4寸)",
        cake_type="chiffon",
        category="base",
        size="4inch",
        format="full",
        is_preset=True,
        steps=[
            "Separate egg",
            "Whisk yolk + sugar + oil + milk",
            "Sift in flour, mix until smooth",
            "Whip white with sugar to stiff peaks",
            "Fold together gently",
            "Pour into ungreased pan",
            "Bake at 320F (160C) for 30-35 minutes",
            "Invert immediately, cool completely",
        ],
        ingredients=[
            _make_ingredient("egg", "鸡蛋", 1, "pc", "main", 0, is_scalable=False),
            _make_ingredient("milk", "奶", 12, "g", "main", 1),
            _make_ingredient("vegetable oil", "油", 10, "g", "main", 2),
            _make_ingredient("cake flour", "低筋面粉", 19, "g", "main", 3),
            _make_ingredient("sugar", "糖", 12, "g", "main", 4),
        ],
    ))

    # 4. Basic Chiffon 6-inch (6inch, base)
    recipes.append(BakingRecipe(
        name="Basic Chiffon 6-inch",
        name_zh="基础戚风(6寸)",
        cake_type="chiffon",
        category="base",
        size="6inch",
        format="full",
        is_preset=True,
        steps=[
            "Separate eggs",
            "Whisk yolks + sugar + oil + milk",
            "Sift in flour, mix until smooth",
            "Whip whites with sugar to stiff peaks",
            "Fold 1/3 whites into yolk batter, then fold back",
            "Pour into ungreased pan",
            "Bake at 320F (160C) for 45-50 minutes",
            "Invert immediately, cool completely",
        ],
        ingredients=[
            _make_ingredient("eggs", "鸡蛋", 3, "pc", "main", 0, is_scalable=False),
            _make_ingredient("milk", "奶", 30, "g", "main", 1),
            _make_ingredient("vegetable oil", "油", 25, "g", "main", 2),
            _make_ingredient("cake flour", "低筋面粉", 45, "g", "main", 3),
            _make_ingredient("sugar", "糖", 30, "g", "main", 4),
        ],
    ))

    # 5. Matcha Chiffon (6-inch, base)
    recipes.append(BakingRecipe(
        name="Matcha Chiffon",
        name_zh="抹茶戚风",
        cake_type="chiffon",
        category="base",
        size="6inch",
        format="full",
        is_preset=True,
        steps=[
            "Separate eggs",
            "Whisk yolks + sugar + oil + milk",
            "Sift in flour + matcha powder, mix until smooth",
            "Whip whites with sugar to stiff peaks",
            "Fold 1/3 whites into yolk batter, then fold back",
            "Pour into ungreased pan",
            "Bake at 320F (160C) for 45-50 minutes",
            "Invert immediately, cool completely",
        ],
        ingredients=[
            _make_ingredient("eggs", "鸡蛋", 3, "pc", "main", 0, is_scalable=False),
            _make_ingredient("milk", "奶", 30, "g", "main", 1),
            _make_ingredient("vegetable oil", "油", 25, "g", "main", 2),
            _make_ingredient("cake flour", "低筋面粉", 39, "g", "main", 3),
            _make_ingredient("sugar", "糖", 30, "g", "main", 4),
            _make_ingredient("matcha powder", "抹茶粉", 6, "g", "main", 5),
        ],
    ))

    # 6. Cocoa Chiffon (6-inch, base)
    recipes.append(BakingRecipe(
        name="Cocoa Chiffon",
        name_zh="可可戚风",
        cake_type="chiffon",
        category="base",
        size="6inch",
        format="full",
        is_preset=True,
        steps=[
            "Separate eggs",
            "Whisk yolks + sugar + oil + milk",
            "Sift in flour + cocoa powder, mix until smooth",
            "Whip whites with sugar to stiff peaks",
            "Fold 1/3 whites into yolk batter, then fold back",
            "Pour into ungreased pan",
            "Bake at 320F (160C) for 45-50 minutes",
            "Invert immediately, cool completely",
        ],
        ingredients=[
            _make_ingredient("eggs", "鸡蛋", 3, "pc", "main", 0, is_scalable=False),
            _make_ingredient("milk", "奶", 30, "g", "main", 1),
            _make_ingredient("vegetable oil", "油", 25, "g", "main", 2),
            _make_ingredient("cake flour", "低筋面粉", 35, "g", "main", 3),
            _make_ingredient("sugar", "糖", 30, "g", "main", 4),
            _make_ingredient("cocoa powder", "可可粉", 10, "g", "main", 5),
        ],
    ))

    # 7. Black Sesame Chiffon (6-inch, base)
    recipes.append(BakingRecipe(
        name="Black Sesame Chiffon",
        name_zh="黑芝麻戚风",
        cake_type="chiffon",
        category="base",
        size="6inch",
        format="full",
        is_preset=True,
        steps=[
            "Separate eggs",
            "Whisk yolks + sugar + oil + milk",
            "Mix black sesame paste into yolk batter",
            "Sift in flour, mix until smooth",
            "Whip whites with sugar to stiff peaks",
            "Fold 1/3 whites into yolk batter, then fold back",
            "Pour into ungreased pan",
            "Bake at 320F (160C) for 45-50 minutes",
            "Invert immediately, cool completely",
        ],
        ingredients=[
            _make_ingredient("eggs", "鸡蛋", 3, "pc", "main", 0, is_scalable=False),
            _make_ingredient("milk", "牛奶", 60, "g", "main", 1),
            _make_ingredient("vegetable oil", "玉米油", 30, "g", "main", 2),
            _make_ingredient("cake flour", "低筋面粉", 55, "g", "main", 3),
            _make_ingredient("sugar", "糖", 45, "g", "main", 4),
            _make_ingredient("black sesame paste", "黑芝麻酱", 30, "g", "main", 5),
        ],
    ))

    # 8. Basic Whipped Cream (universal, cream)
    recipes.append(BakingRecipe(
        name="Basic Whipped Cream",
        name_zh="基础淡奶油",
        cake_type="cream_cake",
        category="cream",
        size="universal",
        format="full",
        is_preset=True,
        steps=[
            "Chill bowl and whisk",
            "Whip heavy cream with sugar to medium-stiff peaks",
            "Use immediately or refrigerate up to 2 hours",
        ],
        ingredients=[
            _make_ingredient("heavy cream", "淡奶油", 250, "g", "main", 0),
            _make_ingredient("sugar", "糖", 20, "g", "main", 1),
        ],
    ))

    # 9. Salty Soy Milk Cream (universal, cream)
    recipes.append(BakingRecipe(
        name="Salty Soy Milk Cream",
        name_zh="咸豆乳奶油",
        cake_type="cream_cake",
        category="cream",
        size="universal",
        format="full",
        is_preset=True,
        steps=[
            "Soften cream cheese to room temp",
            "Beat cream cheese until smooth",
            "Add sugar and sea salt, mix well",
            "Gradually add heavy cream, whip to medium peaks",
            "Fold in soy flour gently",
        ],
        ingredients=[
            _make_ingredient("cream cheese", "奶油奶酪", 100, "g", "main", 0),
            _make_ingredient("heavy cream", "奶油", 200, "g", "main", 1),
            _make_ingredient("sugar", "糖", 25, "g", "main", 2),
            _make_ingredient("sea salt", "海盐", 1.5, "g", "main", 3),
            _make_ingredient("soy flour", "黄豆粉", 20, "g", "main", 4),
        ],
    ))

    return recipes


def seed_baking_data(db: Session) -> dict[str, int]:
    """Seed preset recipes and home inventory into the database.

    Args:
        db: Database session.

    Returns:
        Dict with counts of seeded recipes and inventory items.
    """
    result = {"recipes": 0, "ingredients": 0, "inventory": 0}

    # Seed recipes (skip if any preset recipes exist)
    existing = db.query(BakingRecipe).filter(BakingRecipe.is_preset.is_(True)).count()
    if existing == 0:
        recipes = _build_preset_recipes()
        for recipe in recipes:
            db.add(recipe)
            result["recipes"] += 1
            result["ingredients"] += len(recipe.ingredients)
        db.flush()
        logger.info("Seeded %d preset recipes with %d ingredients",
                     result["recipes"], result["ingredients"])

    # Seed home inventory (skip if any items exist)
    inv_count = db.query(HomeInventory).count()
    if inv_count == 0:
        for name, name_zh, category in INVENTORY_ITEMS:
            db.add(HomeInventory(
                name=name,
                name_zh=name_zh,
                category=category,
                in_stock=True,
                amount=None,
                unit=None,
            ))
            result["inventory"] += 1
        db.flush()
        logger.info("Seeded %d home inventory items", result["inventory"])

    db.commit()
    return result
