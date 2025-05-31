from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
import math

from app.models.models import Meal, MealIngredient, Ingredient


def calculate_available_portions(db: Session, meal_id: int) -> Dict[str, Any]:
    """
    Calculate how many portions of a meal can be made with available ingredients.

    This is a standalone function that can be used independently of the CRUD operations.
    It provides detailed information about available portions and limiting ingredients.

    Args:
        db: Database session
        meal_id: ID of the meal to calculate portions for

    Returns:
        Dictionary with meal information, available portions, and limiting ingredients
    """
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    meal_ingredients = (
        db.query(MealIngredient).filter(MealIngredient.meal_id == meal_id).all()
    )

    if not meal_ingredients:
        return {
            "meal_id": meal.id,
            "meal_name": meal.name,
            "available_portions": 0,
            "limiting_ingredients": [],
        }

    # Calculate available portions for each ingredient
    ingredient_portions = []

    for meal_ingredient in meal_ingredients:
        ingredient = (
            db.query(Ingredient)
            .filter(Ingredient.id == meal_ingredient.ingredient_id)
            .first()
        )

        if not ingredient:
            continue

        if ingredient.quantity <= 0 or meal_ingredient.quantity <= 0:
            # Can't make any portions if any ingredient is missing or required amount is zero
            ingredient_portions.append(
                {
                    "ingredient_id": ingredient.id,
                    "ingredient_name": ingredient.name,
                    "available_quantity": ingredient.quantity,
                    "required_per_portion": meal_ingredient.quantity,
                    "max_portions": 0,
                }
            )
            continue

        # Calculate how many portions can be made with this ingredient
        max_portions = math.floor(ingredient.quantity / meal_ingredient.quantity)

        ingredient_portions.append(
            {
                "ingredient_id": ingredient.id,
                "ingredient_name": ingredient.name,
                "available_quantity": ingredient.quantity,
                "required_per_portion": meal_ingredient.quantity,
                "max_portions": max_portions,
            }
        )

    # Sort ingredients by available portions (ascending)
    ingredient_portions.sort(key=lambda x: x["max_portions"])

    # The maximum number of portions is limited by the ingredient with the least available portions
    max_available_portions = (
        ingredient_portions[0]["max_portions"] if ingredient_portions else 0
    )

    # Get the limiting ingredients (those with the lowest available portions)
    limiting_ingredients = []
    for ingredient_portion in ingredient_portions:
        if ingredient_portion["max_portions"] <= max_available_portions * 1.5:
            # Consider ingredients with portions close to the minimum as limiting
            limiting_ingredients.append(
                {
                    "id": ingredient_portion["ingredient_id"],
                    "name": ingredient_portion["ingredient_name"],
                    "available": ingredient_portion["available_quantity"],
                    "required_per_portion": ingredient_portion["required_per_portion"],
                    "max_portions": ingredient_portion["max_portions"],
                }
            )

        # Limit to top 3 limiting ingredients
        if len(limiting_ingredients) >= 3:
            break

    return {
        "meal_id": meal.id,
        "meal_name": meal.name,
        "available_portions": max_available_portions,
        "limiting_ingredients": limiting_ingredients,
    }


def calculate_all_meals_portions(db: Session) -> List[Dict[str, Any]]:
    """
    Calculate available portions for all meals in the database.

    Args:
        db: Database session

    Returns:
        List of dictionaries with meal information and available portions
    """
    meals = db.query(Meal).all()
    result = []

    for meal in meals:
        try:
            portion_info = calculate_available_portions(db, meal.id)
            result.append(portion_info)
        except HTTPException:
            # Skip meals that cause errors
            continue

    # Sort by available portions (descending)
    result.sort(key=lambda x: x["available_portions"], reverse=True)

    return result


def check_ingredient_impact(db: Session, ingredient_id: int) -> List[Dict[str, Any]]:
    """
    Check which meals would be impacted by changes to a specific ingredient.

    Args:
        db: Database session
        ingredient_id: ID of the ingredient to check

    Returns:
        List of dictionaries with meal information and impact details
    """
    # Find all meals that use this ingredient
    meal_ingredients = (
        db.query(MealIngredient)
        .filter(MealIngredient.ingredient_id == ingredient_id)
        .all()
    )

    if not meal_ingredients:
        return []

    result = []
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()

    if not ingredient:
        return []

    for meal_ingredient in meal_ingredients:
        meal = db.query(Meal).filter(Meal.id == meal_ingredient.meal_id).first()
        if not meal:
            continue

        # Calculate current available portions
        current_portions = calculate_available_portions(db, meal.id)

        # Calculate how many portions this ingredient allows
        max_portions_from_ingredient = (
            math.floor(ingredient.quantity / meal_ingredient.quantity)
            if meal_ingredient.quantity > 0
            else 0
        )

        # Check if this ingredient is limiting the meal
        is_limiting = (
            max_portions_from_ingredient <= current_portions["available_portions"]
        )

        result.append(
            {
                "meal_id": meal.id,
                "meal_name": meal.name,
                "ingredient_required_per_portion": meal_ingredient.quantity,
                "current_available_portions": current_portions["available_portions"],
                "portions_limited_by_this_ingredient": max_portions_from_ingredient,
                "is_limiting_ingredient": is_limiting,
            }
        )

    # Sort by impact (limiting ingredients first, then by available portions)
    result.sort(
        key=lambda x: (not x["is_limiting_ingredient"], x["current_available_portions"])
    )

    return result
