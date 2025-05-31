from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
import calendar

from app.crud.base import CRUDBase
from app.models.models import (
    MonthlyReport,
    MealServing,
    Meal,
    Ingredient,
    MealIngredient,
    Alert,
    AlertType,
)
from app.schemas.reports import MonthlyReportCreate, MonthlyReportUpdate
from app.core.portion_calculator import calculate_all_meals_portions


class CRUDMonthlyReport(
    CRUDBase[MonthlyReport, MonthlyReportCreate, MonthlyReportUpdate]
):
    def get_by_month_year(
        self, db: Session, *, month: int, year: int
    ) -> Optional[MonthlyReport]:
        """Get monthly report by month and year"""
        return (
            db.query(MonthlyReport)
            .filter(MonthlyReport.month == month, MonthlyReport.year == year)
            .first()
        )

    def create_or_update_monthly_report(
        self, db: Session, *, month: int, year: int
    ) -> MonthlyReport:
        """
        Create or update monthly report for the specified month and year
        """
        # Check if report already exists
        report = self.get_by_month_year(db, month=month, year=year)

        # Calculate total portions served
        start_date = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)

        # Get total portions served in the month
        total_portions_served = (
            db.query(func.sum(MealServing.portions))
            .filter(
                func.date(MealServing.served_at) >= start_date,
                func.date(MealServing.served_at) <= end_date,
            )
            .scalar()
            or 0
        )

        # Calculate total portions possible
        meals_portions = calculate_all_meals_portions(db)
        total_portions_possible = sum(
            meal["available_portions"] for meal in meals_portions
        )

        # Calculate difference percentage
        difference_percentage = 0.0
        if total_portions_possible > 0:
            difference_percentage = (
                (total_portions_possible - total_portions_served)
                / total_portions_possible
            ) * 100

        if report:
            # Update existing report
            update_data = {
                "total_portions_served": total_portions_served,
                "total_portions_possible": total_portions_possible,
                "difference_percentage": difference_percentage,
            }
            report = self.update(db, db_obj=report, obj_in=update_data)
        else:
            # Create new report
            report_data = {
                "month": month,
                "year": year,
                "total_portions_served": total_portions_served,
                "total_portions_possible": total_portions_possible,
                "difference_percentage": difference_percentage,
            }
            report = self.create(db, obj_in=MonthlyReportCreate(**report_data))

        # Check if difference percentage is suspicious
        if difference_percentage > 15.0:
            # Create alert
            alert = Alert(
                message=f"Suspicious usage detected in {calendar.month_name[month]} {year}: {difference_percentage:.2f}% difference",
                alert_type=AlertType.usage_suspicious,
                related_report_id=report.id,
            )
            db.add(alert)
            db.commit()

        return report

    def get_ingredient_usage_data(
        self, db: Session, *, ingredient_id: int, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """
        Get usage data for a specific ingredient in a date range
        """
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if not ingredient:
            return {
                "ingredient_id": ingredient_id,
                "ingredient_name": "Unknown",
                "usage_data": [],
                "delivery_data": [],
            }

        # Get all meal servings in the date range
        meal_servings = (
            db.query(MealServing)
            .filter(
                func.date(MealServing.served_at) >= start_date,
                func.date(MealServing.served_at) <= end_date,
            )
            .all()
        )

        # Get all meal ingredients that use this ingredient
        meal_ingredients = (
            db.query(MealIngredient)
            .filter(MealIngredient.ingredient_id == ingredient_id)
            .all()
        )

        # Calculate usage per day
        usage_data = []
        current_date = start_date
        while current_date <= end_date:
            daily_usage = 0

            # Calculate usage for each meal serving on this day
            for serving in meal_servings:
                if func.date(serving.served_at) == current_date:
                    # Find if this meal uses the ingredient
                    for meal_ingredient in meal_ingredients:
                        if meal_ingredient.meal_id == serving.meal_id:
                            # Calculate usage: portions * quantity per portion
                            daily_usage += serving.portions * meal_ingredient.quantity

            usage_data.append({"date": current_date.isoformat(), "usage": daily_usage})

            # Move to next day
            current_date = date.fromordinal(current_date.toordinal() + 1)

        # Get delivery data
        from app.models.models import IngredientDelivery

        deliveries = (
            db.query(IngredientDelivery)
            .filter(
                IngredientDelivery.ingredient_id == ingredient_id,
                func.date(IngredientDelivery.delivery_date) >= start_date,
                func.date(IngredientDelivery.delivery_date) <= end_date,
            )
            .all()
        )

        delivery_data = [
            {
                "date": delivery.delivery_date.date().isoformat(),
                "quantity": delivery.quantity,
            }
            for delivery in deliveries
        ]

        return {
            "ingredient_id": ingredient.id,
            "ingredient_name": ingredient.name,
            "usage_data": usage_data,
            "delivery_data": delivery_data,
        }

    def get_meal_serving_data(
        self, db: Session, *, meal_id: int, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """
        Get serving data for a specific meal in a date range
        """
        meal = db.query(Meal).filter(Meal.id == meal_id).first()
        if not meal:
            return {"meal_id": meal_id, "meal_name": "Unknown", "serving_data": []}

        # Get all meal servings for this meal in the date range
        meal_servings = (
            db.query(MealServing)
            .filter(
                MealServing.meal_id == meal_id,
                func.date(MealServing.served_at) >= start_date,
                func.date(MealServing.served_at) <= end_date,
            )
            .all()
        )

        # Calculate servings per day
        serving_data = []
        current_date = start_date
        while current_date <= end_date:
            daily_portions = 0

            # Calculate portions served on this day
            for serving in meal_servings:
                if func.date(serving.served_at) == current_date:
                    daily_portions += serving.portions

            serving_data.append(
                {"date": current_date.isoformat(), "portions": daily_portions}
            )

            # Move to next day
            current_date = date.fromordinal(current_date.toordinal() + 1)

        return {
            "meal_id": meal.id,
            "meal_name": meal.name,
            "serving_data": serving_data,
        }

    def get_monthly_report_data(
        self, db: Session, *, month: int, year: int
    ) -> Dict[str, Any]:
        """
        Get detailed data for monthly report
        """
        # Ensure report exists
        report = self.create_or_update_monthly_report(db, month=month, year=year)

        # Get date range for the month
        start_date = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)

        # Get all meals
        meals = db.query(Meal).all()

        # Get serving data for each meal
        meals_data = []
        for meal in meals:
            meal_data = self.get_meal_serving_data(
                db, meal_id=meal.id, start_date=start_date, end_date=end_date
            )

            # Calculate total portions for this meal
            total_portions = sum(day["portions"] for day in meal_data["serving_data"])

            meals_data.append(
                {
                    "meal_id": meal.id,
                    "meal_name": meal.name,
                    "total_portions": total_portions,
                    "daily_data": meal_data["serving_data"],
                }
            )

        # Sort meals by total portions (descending)
        meals_data.sort(key=lambda x: x["total_portions"], reverse=True)

        # Get all ingredients
        ingredients = db.query(Ingredient).all()

        # Get usage data for each ingredient
        ingredients_data = []
        for ingredient in ingredients:
            ingredient_data = self.get_ingredient_usage_data(
                db,
                ingredient_id=ingredient.id,
                start_date=start_date,
                end_date=end_date,
            )

            # Calculate total usage for this ingredient
            total_usage = sum(day["usage"] for day in ingredient_data["usage_data"])
            total_delivery = sum(
                delivery["quantity"] for delivery in ingredient_data["delivery_data"]
            )

            ingredients_data.append(
                {
                    "ingredient_id": ingredient.id,
                    "ingredient_name": ingredient.name,
                    "total_usage": total_usage,
                    "total_delivery": total_delivery,
                    "daily_usage": ingredient_data["usage_data"],
                    "deliveries": ingredient_data["delivery_data"],
                }
            )

        # Sort ingredients by total usage (descending)
        ingredients_data.sort(key=lambda x: x["total_usage"], reverse=True)

        return {
            "month": month,
            "year": year,
            "month_name": calendar.month_name[month],
            "total_portions_served": report.total_portions_served,
            "total_portions_possible": report.total_portions_possible,
            "difference_percentage": report.difference_percentage,
            "meals_data": meals_data,
            "ingredients_data": ingredients_data,
        }


monthly_report = CRUDMonthlyReport(MonthlyReport)
