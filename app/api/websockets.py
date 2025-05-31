from typing import List, Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json
import asyncio
from datetime import datetime

from app.db.session import SessionLocal
from app.models.models import Ingredient, Alert, AlertType


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[Dict[str, Any]] = []

    async def connect(self, websocket: WebSocket, client_id: str, role: str):
        await websocket.accept()
        self.active_connections.append(
            {"websocket": websocket, "client_id": client_id, "role": role}
        )

    def disconnect(self, websocket: WebSocket):
        for i, connection in enumerate(self.active_connections):
            if connection["websocket"] == websocket:
                self.active_connections.pop(i)
                break

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection["websocket"].send_text(message)

    async def broadcast_to_role(self, message: str, role: str):
        for connection in self.active_connections:
            if connection["role"] == role:
                await connection["websocket"].send_text(message)

    async def broadcast_inventory_update(
        self, ingredient_id: int, ingredient_name: str, quantity: float
    ):
        message = json.dumps(
            {
                "type": "inventory_update",
                "data": {
                    "ingredient_id": ingredient_id,
                    "ingredient_name": ingredient_name,
                    "quantity": quantity,
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )
        await self.broadcast(message)

    async def broadcast_alert(
        self, alert_type: str, message: str, related_id: Optional[int] = None
    ):
        alert_data = {
            "type": "alert",
            "data": {
                "alert_type": alert_type,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            },
        }

        if related_id:
            alert_data["data"]["related_id"] = related_id

        await self.broadcast(json.dumps(alert_data))

    async def broadcast_low_stock_alert(
        self,
        ingredient_id: int,
        ingredient_name: str,
        quantity: float,
        min_quantity: float,
    ):
        message = json.dumps(
            {
                "type": "low_stock_alert",
                "data": {
                    "ingredient_id": ingredient_id,
                    "ingredient_name": ingredient_name,
                    "current_quantity": quantity,
                    "min_quantity": min_quantity,
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )
        await self.broadcast(message)


manager = ConnectionManager()


async def check_low_stock():
    """Background task to check for low stock ingredients and send alerts"""
    while True:
        try:
            db = SessionLocal()
            # Get all ingredients with quantity below min_quantity
            low_stock_ingredients = (
                db.query(Ingredient)
                .filter(Ingredient.quantity < Ingredient.min_quantity)
                .all()
            )

            for ingredient in low_stock_ingredients:
                # Create alert in database
                alert = Alert(
                    message=f"Low stock alert: {ingredient.name} is below minimum quantity ({ingredient.quantity}g < {ingredient.min_quantity}g)",
                    alert_type=AlertType.ingredient_low,
                    related_ingredient_id=ingredient.id,
                )
                db.add(alert)

                # Send real-time alert via WebSocket
                await manager.broadcast_low_stock_alert(
                    ingredient_id=ingredient.id,
                    ingredient_name=ingredient.name,
                    quantity=ingredient.quantity,
                    min_quantity=ingredient.min_quantity,
                )

            db.commit()
            db.close()
        except Exception as e:
            print(f"Error in check_low_stock: {e}")
            if "db" in locals():
                db.close()

        # Check every 5 minutes
        await asyncio.sleep(300)


async def start_background_tasks():
    """Start background tasks for WebSocket notifications"""
    asyncio.create_task(check_low_stock())
