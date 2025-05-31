from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas import ingredient as schemas
from app.models import models
from app.crud import crud_meal, crud_ingredient
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Meal])
def read_meals(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Retrieve meals.
    """
    meals = crud_meal.meal.get_multi(db, skip=skip, limit=limit)
    return meals


@router.post("/", response_model=schemas.Meal)
def create_meal(
    *,
    db: Session = Depends(deps.get_db),
    meal_in: schemas.MealCreate,
    current_user: models.User = Depends(deps.get_current_active_user_with_permission),
):
    """
    Create new meal with ingredients.
    """
    meal = crud_meal.meal.get_by_name(db, name=meal_in.name)
    if meal:
        raise HTTPException(
            status_code=400,
            detail="Meal with this name already exists",
        )

    # Check if all ingredients exist
    for ingredient_item in meal_in.ingredients:
        ingredient = crud_ingredient.ingredient.get(
            db, id=ingredient_item.ingredient_id
        )
        if not ingredient:
            raise HTTPException(
                status_code=404,
                detail=f"Ingredient with id {ingredient_item.ingredient_id} not found",
            )

    meal = crud_meal.meal.create_with_ingredients(
        db, obj_in=meal_in, user_id=current_user.id
    )
    return meal


@router.put("/{id}", response_model=schemas.Meal)
def update_meal(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    meal_in: schemas.MealUpdate,
    current_user: models.User = Depends(deps.get_current_active_user_with_permission),
):
    """
    Update a meal.
    """
    meal = crud_meal.meal.get(db, id=id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    # Check if all ingredients exist if ingredients are being updated
    if meal_in.ingredients:
        for ingredient_item in meal_in.ingredients:
            ingredient = crud_ingredient.ingredient.get(
                db, id=ingredient_item.ingredient_id
            )
            if not ingredient:
                raise HTTPException(
                    status_code=404,
                    detail=f"Ingredient with id {ingredient_item.ingredient_id} not found",
                )

    meal = crud_meal.meal.update_with_ingredients(db, db_obj=meal, obj_in=meal_in)
    return meal


@router.get("/{id}", response_model=schemas.Meal)
def read_meal(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get meal by ID.
    """
    meal = crud_meal.meal.get_with_ingredients(db, id=id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    return meal


@router.delete("/{id}", response_model=schemas.Meal)
def delete_meal(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user_with_permission),
):
    """
    Delete a meal.
    """
    meal = crud_meal.meal.get(db, id=id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    meal = crud_meal.meal.remove(db, id=id)
    return meal
