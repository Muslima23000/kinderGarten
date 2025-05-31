from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.models import MealServing, Meal, MealIngredient, Ingredient
from app.schemas.meal_serving import MealServingCreate, MealServingUpdate
from sqlalchemy import func


class CRUDMealServing(CRUDBase[MealServing, MealServingCreate, MealServingUpdate]):
    def create_with_user(
        self, db: Session, *, obj_in: MealServingCreate, user_id: int
    ) -> MealServing:
        """
        Create a meal serving record and deduct ingredients from inventory
        """
        # Get the meal with its ingredients
        meal = db.query(Meal).filter(Meal.id == obj_in.meal_id).first()
        if not meal:
            return None

        # Get all meal ingredients
        meal_ingredients = (
            db.query(MealIngredient)
            .filter(MealIngredient.meal_id == obj_in.meal_id)
            .all()
        )

        # Check if there are enough ingredients
        for meal_ingredient in meal_ingredients:
            ingredient = (
                db.query(Ingredient)
                .filter(Ingredient.id == meal_ingredient.ingredient_id)
                .first()
            )

            required_quantity = meal_ingredient.quantity * obj_in.portions
            if ingredient.quantity < required_quantity:
                # Not enough ingredients
                return None

        # Deduct ingredients from inventory
        for meal_ingredient in meal_ingredients:
            ingredient = (
                db.query(Ingredient)
                .filter(Ingredient.id == meal_ingredient.ingredient_id)
                .first()
            )

            required_quantity = meal_ingredient.quantity * obj_in.portions
            ingredient.quantity -= required_quantity
            db.add(ingredient)

        # Create meal serving record
        db_obj = MealServing(
            meal_id=obj_in.meal_id,
            portions=obj_in.portions,
            served_by=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_meal(
        self, db: Session, *, meal_id: int, skip: int = 0, limit: int = 100
    ) -> List[MealServing]:
        return (
            db.query(MealServing)
            .filter(MealServing.meal_id == meal_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[MealServing]:
        return (
            db.query(MealServing)
            .filter(MealServing.served_by == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def calculate_available_portions(
        self, db: Session, *, meal_id: int
    ) -> Dict[str, Any]:
        """
        Calculate how many portions of a meal can be made with available ingredients
        """
        meal = db.query(Meal).filter(Meal.id == meal_id).first()
        if not meal:
            return {"available_portions": 0, "limiting_ingredients": []}

        meal_ingredients = (
            db.query(MealIngredient).filter(MealIngredient.meal_id == meal_id).all()
        )

        if not meal_ingredients:
            return {"available_portions": 0, "limiting_ingredients": []}

        available_portions = []
        limiting_ingredients = []

        for meal_ingredient in meal_ingredients:
            ingredient = (
                db.query(Ingredient)
                .filter(Ingredient.id == meal_ingredient.ingredient_id)
                .first()
            )

            if ingredient.quantity <= 0 or meal_ingredient.quantity <= 0:
                # Can't make any portions if any ingredient is missing
                limiting_ingredients.append(
                    {
                        "id": ingredient.id,
                        "name": ingredient.name,
                        "available": ingredient.quantity,
                        "required_per_portion": meal_ingredient.quantity,
                        "max_portions": 0,
                    }
                )
                available_portions.append(0)
                continue

            # Calculate how many portions can be made with this ingredient
            max_portions = int(ingredient.quantity / meal_ingredient.quantity)
            available_portions.append(max_portions)

            # If this is a limiting ingredient, add it to the list
            if max_portions < 10:  # Arbitrary threshold for "limiting"
                limiting_ingredients.append(
                    {
                        "id": ingredient.id,
                        "name": ingredient.name,
                        "available": ingredient.quantity,
                        "required_per_portion": meal_ingredient.quantity,
                        "max_portions": max_portions,
                    }
                )

        # The maximum number of portions is limited by the ingredient with the least available portions
        max_available_portions = min(available_portions) if available_portions else 0

        # Sort limiting ingredients by available portions
        limiting_ingredients.sort(key=lambda x: x["max_portions"])

        return {
            "meal_id": meal.id,
            "meal_name": meal.name,
            "available_portions": max_available_portions,
            "limiting_ingredients": limiting_ingredients[
                :3
            ],  # Return top 3 limiting ingredients
        }


meal_serving = CRUDMealServing(MealServing)
