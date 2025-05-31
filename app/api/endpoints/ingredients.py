from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import models
from app.crud import crud_ingredient as crud
from app.schemas import ingredient as schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Ingredient])
def read_ingredients(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Retrieve ingredients.
    """
    ingredients = crud.ingredient.get_multi(db, skip=skip, limit=limit)
    return ingredients


@router.post("/", response_model=schemas.Ingredient)
def create_ingredient(
    *,
    db: Session = Depends(deps.get_db),
    ingredient_in: schemas.IngredientCreate,
    current_user: models.User = Depends(deps.get_current_active_user_with_permission),
):
    """
    Create new ingredient.
    """
    ingredient = crud.ingredient.get_by_name(db, name=ingredient_in.name)
    if ingredient:
        raise HTTPException(
            status_code=400,
            detail="Ingredient with this name already exists",
        )
    ingredient = crud.ingredient.create(db, obj_in=ingredient_in)
    return ingredient


@router.put("/{id}", response_model=schemas.Ingredient)
def update_ingredient(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    ingredient_in: schemas.IngredientUpdate,
    current_user: models.User = Depends(deps.get_current_active_user_with_permission),
):
    """
    Update an ingredient.
    """
    ingredient = crud.ingredient.get(db, id=id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    ingredient = crud.ingredient.update(db, db_obj=ingredient, obj_in=ingredient_in)
    return ingredient


@router.get("/{id}", response_model=schemas.Ingredient)
def read_ingredient(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get ingredient by ID.
    """
    ingredient = crud.ingredient.get(db, id=id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.delete("/{id}", response_model=schemas.Ingredient)
def delete_ingredient(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user_with_permission),
):
    """
    Delete an ingredient.
    """
    ingredient = crud.ingredient.get(db, id=id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    ingredient = crud.ingredient.remove(db, id=id)
    return ingredient


@router.post("/delivery/", response_model=schemas.IngredientDelivery)
def create_ingredient_delivery(
    *,
    db: Session = Depends(deps.get_db),
    delivery_in: schemas.IngredientDeliveryCreate,
    current_user: models.User = Depends(deps.get_current_active_user_with_permission),
):
    """
    Create new ingredient delivery.
    """
    ingredient = crud.ingredient.get(db, id=delivery_in.ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    delivery = crud.ingredient_delivery.create_with_user(
        db, obj_in=delivery_in, user_id=current_user.id
    )
    return delivery


@router.get("/delivery/", response_model=List[schemas.IngredientDelivery])
def read_ingredient_deliveries(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Retrieve ingredient deliveries.
    """
    deliveries = crud.ingredient_delivery.get_multi(db, skip=skip, limit=limit)
    return deliveries


@router.get("/delivery/{id}", response_model=schemas.IngredientDelivery)
def read_ingredient_delivery(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get ingredient delivery by ID.
    """
    delivery = crud.ingredient_delivery.get(db, id=id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Ingredient delivery not found")
    return delivery


@router.get("/check-low-stock/", response_model=List[schemas.Ingredient])
def check_low_stock(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Check for ingredients with low stock.
    """
    low_stock_ingredients = crud.ingredient.check_low_stock(db)
    return low_stock_ingredients
