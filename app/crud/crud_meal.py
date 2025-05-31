from typing import List, Optional, Dict, Any

from app.crud.base import CRUDBase
from app.models.models import Meal, MealIngredient
from app.schemas.ingredient import MealCreate, MealUpdate, MealIngredientCreate
from sqlalchemy.orm import Session


class CRUDMeal(CRUDBase[Meal, MealCreate, MealUpdate]):
    def create_with_ingredients(
        self, db: Session, *, obj_in: MealCreate, user_id: int
    ) -> Meal:
        # Create meal
        db_obj = Meal(
            name=obj_in.name,
            description=obj_in.description,
            created_by=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Add ingredients
        for ingredient_data in obj_in.ingredients:
            meal_ingredient = MealIngredient(
                meal_id=db_obj.id,
                ingredient_id=ingredient_data.ingredient_id,
                quantity=ingredient_data.quantity,
            )
            db.add(meal_ingredient)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_with_ingredients(
        self, db: Session, *, db_obj: Meal, obj_in: MealUpdate
    ) -> Meal:
        update_data = obj_in.dict(exclude_unset=True)
        
        # Update meal basic info
        if "name" in update_data:
            db_obj.name = update_data["name"]
        if "description" in update_data:
            db_obj.description = update_data["description"]
        
        # Update ingredients if provided
        if "ingredients" in update_data and update_data["ingredients"] is not None:
            # Remove existing ingredients
            db.query(MealIngredient).filter(MealIngredient.meal_id == db_obj.id).delete()
            
            # Add new ingredients
            for ingredient_data in update_data["ingredients"]:
                meal_ingredient = MealIngredient(
                    meal_id=db_obj.id,
                    ingredient_id=ingredient_data["ingredient_id"],
                    quantity=ingredient_data["quantity"],
                )
                db.add(meal_ingredient)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_name(self, db: Session, *, name: str) -> Optional[Meal]:
        return db.query(Meal).filter(Meal.name == name).first()

    def get_with_ingredients(self, db: Session, *, id: int) -> Optional[Meal]:
        return db.query(Meal).filter(Meal.id == id).first()


meal = CRUDMeal(Meal)






