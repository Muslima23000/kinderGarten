from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import models
from app.schemas import meal_serving as meal_serving_schema
from app.crud import crud_meal_serving, crud_meal
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[meal_serving_schema.MealServing])
def read_meal_servings(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Retrieve meal servings.
    """
    meal_servings = crud_meal_serving.meal_serving.get_multi(db, skip=skip, limit=limit)
    return meal_servings


@router.post("/", response_model=meal_serving_schema.MealServing)
def create_meal_serving(
    *,
    db: Session = Depends(deps.get_db),
    meal_serving_in: meal_serving_schema.MealServingCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Create new meal serving (serve a meal).
    """
    # Check if meal exists
    meal = crud_meal.meal.get(db, id=meal_serving_in.meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    # Calculate available portions
    portion_info = crud_meal_serving.meal_serving.calculate_available_portions(
        db, meal_id=meal_serving_in.meal_id
    )

    # Check if there are enough ingredients
    if portion_info["available_portions"] < meal_serving_in.portions:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Not enough ingredients for requested portions",
                "available_portions": portion_info["available_portions"],
                "requested_portions": meal_serving_in.portions,
                "limiting_ingredients": portion_info["limiting_ingredients"],
            },
        )

    # Create meal serving
    meal_serving = crud_meal_serving.meal_serving.create_with_user(
        db, obj_in=meal_serving_in, user_id=current_user.id
    )

    if not meal_serving:
        raise HTTPException(status_code=500, detail="Failed to create meal serving")

    return meal_serving


@router.get("/{id}", response_model=meal_serving_schema.MealServing)
def read_meal_serving(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get meal serving by ID.
    """
    meal_serving = crud_meal_serving.meal_serving.get(db, id=id)
    if not meal_serving:
        raise HTTPException(status_code=404, detail="Meal serving not found")
    return meal_serving


@router.get("/by-meal/{meal_id}", response_model=List[meal_serving_schema.MealServing])
def read_meal_servings_by_meal(
    *,
    db: Session = Depends(deps.get_db),
    meal_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get meal servings by meal ID.
    """
    meal_servings = crud_meal_serving.meal_serving.get_by_meal(
        db, meal_id=meal_id, skip=skip, limit=limit
    )
    return meal_servings


@router.get("/by-user/{user_id}", response_model=List[meal_serving_schema.MealServing])
def read_meal_servings_by_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user_with_permission),
):
    """
    Get meal servings by user ID.
    """
    meal_servings = crud_meal_serving.meal_serving.get_by_user(
        db, user_id=user_id, skip=skip, limit=limit
    )
    return meal_servings


@router.get(
    "/calculate-portions/{meal_id}",
    response_model=meal_serving_schema.MealPortionCalculation,
)
def calculate_available_portions(
    *,
    db: Session = Depends(deps.get_db),
    meal_id: int,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Calculate how many portions of a meal can be made with available ingredients.
    """
    meal = crud_meal.meal.get(db, id=meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    portion_info = crud_meal_serving.meal_serving.calculate_available_portions(
        db, meal_id=meal_id
    )

    return portion_info
