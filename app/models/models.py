from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum


from app.db.base_class import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    chef = "chef"
    manager = "manager"


class AlertType(str, enum.Enum):
    ingredient_low = "ingredient_low"
    usage_suspicious = "usage_suspicious"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.chef)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ingredient_deliveries = relationship(
        "IngredientDelivery", back_populates="created_by_user"
    )
    meals = relationship("Meal", back_populates="created_by_user")
    meal_servings = relationship("MealServing", back_populates="served_by_user")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    quantity = Column(Float, default=0.0)  # in grams
    min_quantity = Column(Float, default=0.0)  # in grams, for alerts
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    deliveries = relationship("IngredientDelivery", back_populates="ingredient")
    meal_ingredients = relationship("MealIngredient", back_populates="ingredient")
    alerts = relationship("Alert", back_populates="related_ingredient")


class IngredientDelivery(Base):
    __tablename__ = "ingredient_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    quantity = Column(Float, nullable=False)  # in grams
    delivery_date = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ingredient = relationship("Ingredient", back_populates="deliveries")
    created_by_user = relationship("User", back_populates="ingredient_deliveries")


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    created_by_user = relationship("User", back_populates="meals")
    meal_ingredients = relationship(
        "MealIngredient", back_populates="meal", cascade="all, delete-orphan"
    )
    meal_servings = relationship("MealServing", back_populates="meal")


class MealIngredient(Base):
    __tablename__ = "meal_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    quantity = Column(Float, nullable=False)  # in grams per portion
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    meal = relationship("Meal", back_populates="meal_ingredients")
    ingredient = relationship("Ingredient", back_populates="meal_ingredients")


class MealServing(Base):
    __tablename__ = "meal_servings"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False)
    portions = Column(Integer, nullable=False)
    served_at = Column(DateTime(timezone=True), server_default=func.now())
    served_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    meal = relationship("Meal", back_populates="meal_servings")
    served_by_user = relationship("User", back_populates="meal_servings")


class MonthlyReport(Base):
    __tablename__ = "monthly_reports"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    total_portions_served = Column(Integer, default=0)
    total_portions_possible = Column(Integer, default=0)
    difference_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    alerts = relationship("Alert", back_populates="related_report")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    related_ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=True)
    related_report_id = Column(Integer, ForeignKey("monthly_reports.id"), nullable=True)

    # Relationships
    related_ingredient = relationship("Ingredient", back_populates="alerts")
    related_report = relationship("MonthlyReport", back_populates="alerts")


class Roles(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
