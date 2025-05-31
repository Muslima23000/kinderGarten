from typing import List, Optional, Dict, Any

from app.crud.base import CRUDBase
from app.models.models import Ingredient, IngredientDelivery
from app.schemas.ingredient import (
    IngredientCreate,
    IngredientUpdate,
    IngredientDeliveryCreate,
    IngredientDeliveryUpdate,
)
from sqlalchemy.orm import Session


class CRUDIngredient(CRUDBase[Ingredient, IngredientCreate, IngredientUpdate]):
    def create(self, db: Session, *, obj_in: IngredientCreate) -> Ingredient:
        db_obj = Ingredient(
            name=obj_in.name,
            quantity=obj_in.quantity,
            min_quantity=obj_in.min_quantity,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_name(self, db: Session, *, name: str) -> Optional[Ingredient]:
        return db.query(Ingredient).filter(Ingredient.name == name).first()

    def update_quantity(
        self, db: Session, *, db_obj: Ingredient, quantity_change: float
    ) -> Ingredient:
        """
        Update ingredient quantity by adding (or subtracting if negative) the specified amount
        """
        new_quantity = max(0, db_obj.quantity + quantity_change)
        db_obj.quantity = new_quantity
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def check_low_stock(self, db: Session) -> List[Ingredient]:
        """
        Return all ingredients where quantity is below min_quantity
        """
        return (
            db.query(Ingredient)
            .filter(Ingredient.quantity < Ingredient.min_quantity)
            .all()
        )


class CRUDIngredientDelivery(
    CRUDBase[IngredientDelivery, IngredientDeliveryCreate, IngredientDeliveryUpdate]
):
    def create_with_user(
        self, db: Session, *, obj_in: IngredientDeliveryCreate, user_id: int
    ) -> IngredientDelivery:
        obj_in_data = obj_in.dict()
        db_obj = IngredientDelivery(**obj_in_data, created_by=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Update ingredient quantity
        ingredient = (
            db.query(Ingredient).filter(Ingredient.id == obj_in.ingredient_id).first()
        )
        if ingredient:
            ingredient.quantity += obj_in.quantity
            db.add(ingredient)
            db.commit()

        return db_obj

    def get_by_ingredient(
        self, db: Session, *, ingredient_id: int, skip: int = 0, limit: int = 100
    ) -> List[IngredientDelivery]:
        return (
            db.query(IngredientDelivery)
            .filter(IngredientDelivery.ingredient_id == ingredient_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


ingredient = CRUDIngredient(Ingredient)
ingredient_delivery = CRUDIngredientDelivery(IngredientDelivery)
