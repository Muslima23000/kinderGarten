from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session

from app.api import deps
from app.api.websockets import manager
from app.models.models import UserRole

router = APIRouter()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    token: Optional[str] = None,
):
    """
    WebSocket endpoint for real-time updates.
    """
    # Default role for unauthenticated connections
    role = "guest"

    # Validate token if provided
    if token:
        try:
            # Get database session
            db = next(deps.get_db())

            # Validate token and get user
            from jose import jwt, JWTError
            from app.core.security import ALGORITHM
            from app.core.config import settings

            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
                user_id = int(payload.get("sub"))
                if user_id:
                    user = (
                        db.query(deps.models.User)
                        .filter(deps.models.User.id == user_id)
                        .first()
                    )
                    if user and user.is_active:
                        role = user.role
            except (JWTError, ValueError):
                pass

        except Exception:
            pass

    # Accept connection
    await manager.connect(websocket, client_id, role)

    try:
        # Send initial connection confirmation
        await manager.send_personal_message(
            f"Connected to real-time updates. Role: {role}", websocket
        )

        # Keep connection open and handle messages
        while True:
            data = await websocket.receive_text()
            # Process any client messages if needed
            await manager.send_personal_message(f"Message received", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
