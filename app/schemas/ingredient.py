from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Shared properties
class IngredientBase(BaseModel):
    name: str
    quantity: float = Field(ge=0.0)
    min_quantity: float = Field(ge=0.0)


# Properties to receive on item creation
class IngredientCreate(IngredientBase):
    pass


# Properties to receive on item update
class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[float] = Field(default=None, ge=0.0)
    min_quantity: Optional[float] = Field(default=None, ge=0.0)


# Properties shared by models stored in DB
class IngredientInDBBase(IngredientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Properties to return to client
class Ingredient(IngredientInDBBase):
    pass


# Properties stored in DB
class IngredientInDB(IngredientInDBBase):
    pass


# Ingredient Delivery
class IngredientDeliveryBase(BaseModel):
    ingredient_id: int
    quantity: float = Field(gt=0.0)
    delivery_date: datetime


# Properties to receive on item creation
class IngredientDeliveryCreate(IngredientDeliveryBase):
    pass


# Properties to receive on item update
class IngredientDeliveryUpdate(BaseModel):
    quantity: Optional[float] = Field(default=None, gt=0.0)
    delivery_date: Optional[datetime] = None


# Properties shared by models stored in DB
class IngredientDeliveryInDBBase(IngredientDeliveryBase):
    id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# Properties to return to client
class IngredientDelivery(IngredientDeliveryInDBBase):
    pass


# Properties stored in DB
class IngredientDeliveryInDB(IngredientDeliveryInDBBase):
    pass


# Meal Ingredient
class MealIngredientBase(BaseModel):
    ingredient_id: int
    quantity: float = Field(gt=0.0)  # grams per portion


# Properties to receive on item creation
class MealIngredientCreate(MealIngredientBase):
    pass


# Properties to receive on item update
class MealIngredientUpdate(BaseModel):
    quantity: Optional[float] = Field(default=None, gt=0.0)


# Properties shared by models stored in DB
class MealIngredientInDBBase(MealIngredientBase):
    id: int
    meal_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Properties to return to client
class MealIngredient(MealIngredientInDBBase):
    pass


# Properties stored in DB
class MealIngredientInDB(MealIngredientInDBBase):
    pass


# Meal
class MealBase(BaseModel):
    name: str
    description: Optional[str] = None


# Properties to receive on item creation
class MealCreate(MealBase):
    ingredients: List[MealIngredientCreate]


# Properties to receive on item update
class MealUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[List[MealIngredientCreate]] = None


# Properties shared by models stored in DB
class MealInDBBase(MealBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Properties to return to client
class Meal(MealInDBBase):
    ingredients: List[MealIngredient] = []


# Properties stored in DB
class MealInDB(MealInDBBase):
    pass
