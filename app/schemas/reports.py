from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field


# Monthly Report
class MonthlyReportBase(BaseModel):
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)
    total_portions_served: int = 0
    total_portions_possible: int = 0
    difference_percentage: float = 0.0


# Properties to receive on item creation
class MonthlyReportCreate(MonthlyReportBase):
    pass


# Properties to receive on item update
class MonthlyReportUpdate(BaseModel):
    total_portions_served: Optional[int] = None
    total_portions_possible: Optional[int] = None
    difference_percentage: Optional[float] = None


# Properties shared by models stored in DB
class MonthlyReportInDBBase(MonthlyReportBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Properties to return to client
class MonthlyReport(MonthlyReportInDBBase):
    pass


# Properties stored in DB
class MonthlyReportInDB(MonthlyReportInDBBase):
    pass


# Alert
class AlertBase(BaseModel):
    message: str
    alert_type: str
    is_read: bool = False
    related_ingredient_id: Optional[int] = None
    related_report_id: Optional[int] = None


# Properties to receive on item creation
class AlertCreate(AlertBase):
    pass


# Properties to receive on item update
class AlertUpdate(BaseModel):
    message: Optional[str] = None
    is_read: Optional[bool] = None


# Properties shared by models stored in DB
class AlertInDBBase(AlertBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Properties to return to client
class Alert(AlertInDBBase):
    pass


# Properties stored in DB
class AlertInDB(AlertInDBBase):
    pass


# Visualization data
class IngredientUsageData(BaseModel):
    ingredient_id: int
    ingredient_name: str
    usage_data: List[Dict[str, Any]]
    delivery_data: List[Dict[str, Any]]


class MealServingData(BaseModel):
    meal_id: int
    meal_name: str
    serving_data: List[Dict[str, Any]]


class MonthlyReportData(BaseModel):
    month: int
    year: int
    total_portions_served: int
    total_portions_possible: int
    difference_percentage: float
    meals_data: List[Dict[str, Any]]
    ingredients_data: List[Dict[str, Any]]
