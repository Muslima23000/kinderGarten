from typing import List
from fastapi import APIRouter

from app.api.endpoints.ingredients import router as ingredients_router
from app.api.endpoints.meals import router as meals_router
from app.api.endpoints.meal_servings import router as meal_servings_router
from app.api.endpoints.reports import router as reports_router
from app.api.endpoints.users import router as users_router
from app.api.endpoints.websocket import router as websocket_router

api_router = APIRouter()
api_router.include_router(
    ingredients_router, prefix="/ingredients", tags=["ingredients"]
)
api_router.include_router(meals_router, prefix="/meals", tags=["meals"])
api_router.include_router(
    meal_servings_router, prefix="/meal-servings", tags=["meal-servings"]
)
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(websocket_router, prefix="/ws", tags=["websocket"])
