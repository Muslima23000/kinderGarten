from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.models import models
from app.crud import crud_reports, crud_ingredient, crud_meal
from app.schemas.reports import (
    MonthlyReport,
    MonthlyReportData,
    IngredientUsageData,
    MealServingData,
    Alert,
)
from app.api import deps

router = APIRouter()


@router.get("/monthly/{year}/{month}", response_model=MonthlyReport)
def get_monthly_report(
    *,
    db: Session = Depends(deps.get_db),
    year: int,
    month: int,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get monthly report by year and month.
    """
    report = crud_reports.monthly_report.get_by_month_year(db, month=month, year=year)
    if not report:
        # Create report if it doesn't exist
        report = crud_reports.monthly_report.create_or_update_monthly_report(
            db, month=month, year=year
        )
    return report


@router.post("/monthly/{year}/{month}/generate", response_model=MonthlyReport)
def generate_monthly_report(
    *,
    db: Session = Depends(deps.get_db),
    year: int,
    month: int,
    current_user: models.User = Depends(deps.get_current_active_user_with_permission),
):
    """
    Generate or update monthly report for specified month and year.
    """
    report = crud_reports.monthly_report.create_or_update_monthly_report(
        db, month=month, year=year
    )
    return report


@router.get("/monthly/{year}/{month}/detailed", response_model=MonthlyReportData)
def get_monthly_report_detailed(
    *,
    db: Session = Depends(deps.get_db),
    year: int,
    month: int,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get detailed monthly report data including meal and ingredient statistics.
    """
    report_data = crud_reports.monthly_report.get_monthly_report_data(
        db, month=month, year=year
    )
    return report_data


@router.get("/ingredient/{ingredient_id}/usage", response_model=IngredientUsageData)
def get_ingredient_usage(
    *,
    db: Session = Depends(deps.get_db),
    ingredient_id: int,
    start_date: date,
    end_date: date = None,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get usage data for a specific ingredient in a date range.
    """
    if end_date is None:
        end_date = date.today()

    ingredient = crud_ingredient.ingredient.get(db, id=ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    usage_data = crud.monthly_report.get_ingredient_usage_data(
        db, ingredient_id=ingredient_id, start_date=start_date, end_date=end_date
    )
    return usage_data


@router.get("/meal/{meal_id}/servings", response_model=MealServingData)
def get_meal_servings(
    *,
    db: Session = Depends(deps.get_db),
    meal_id: int,
    start_date: date,
    end_date: date = None,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get serving data for a specific meal in a date range.
    """
    if end_date is None:
        end_date = date.today()

    meal = crud_meal.meal.get(db, id=meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    serving_data = crud_reports.monthly_report.get_meal_serving_data(
        db, meal_id=meal_id, start_date=start_date, end_date=end_date
    )
    return serving_data


@router.get("/alerts/", response_model=List[Alert])
def get_alerts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    current_user: models.User = Depends(deps.get_current_active_user_with_permission),
):

    if unread_only:
        alerts = (
            db.query(models.Alert)
            .filter(models.Alert.is_read == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        alerts = db.query(models.Alert).offset(skip).limit(limit).all()
    return alerts


@router.put("/alerts/{alert_id}/mark-read", response_model=Alert)
def mark_alert_read(
    *,
    db: Session = Depends(deps.get_db),
    alert_id: int,
    current_user: models.User = Depends(deps.get_current_active_user_with_permission),
):
    """
    Mark an alert as read.
    """
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_read = True
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
