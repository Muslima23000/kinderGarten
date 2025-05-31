from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Shared properties
class MealServingBase(BaseModel):
    meal_id: int
    portions: int = Field(gt=0)


# Properties to receive on item creation
class MealServingCreate(MealServingBase):
    pass


# Properties to receive on item update
class MealServingUpdate(BaseModel):
    portions: Optional[int] = Field(default=None, gt=0)


# Properties shared by models stored in DB
class MealServingInDBBase(MealServingBase):
    id: int
    served_by: int
    served_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Properties to return to client
class MealServing(MealServingInDBBase):
    pass


# Properties stored in DB
class MealServingInDB(MealServingInDBBase):
    pass


# Portion Calculation
class MealPortionCalculation(BaseModel):
    meal_id: int
    meal_name: str
    available_portions: int
    limiting_ingredients: List[dict] = []


# Token
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
