# app/notifications/socket_manager.py

import logging
import asyncio
from typing import Dict, Set, Any, Optional

logger = logging.getLogger(__name__)


class NotificationSocketManager:
    """
    Manages real-time WebSocket / Socket.IO connections per user_id.
    Broadcasts live notification events and domain-specific updates.
    """

    def __init__(self):
        self.active_connections: Dict[str, Set[Any]] = {}

    def connect(self, user_id: str, connection: Any):
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(connection)
        logger.info(f"[NOTIFICATION SOCKET] User {user_id} connected to real-time stream.")

    def disconnect(self, user_id: str, connection: Any):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(connection)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"[NOTIFICATION SOCKET] User {user_id} disconnected from stream.")

    async def notify_user(self, user_id: str, payload: dict, event_type: str = "notification"):
        """
        Sends event payload to active user socket sessions.
        """
        if user_id in self.active_connections:
            connections = list(self.active_connections[user_id])
            for conn in connections:
                try:
                    message = {"event": event_type, "data": payload}
                    if hasattr(conn, "send_json"):
                        await conn.send_json(message)
                    elif hasattr(conn, "emit"):
                        await conn.emit(event_type, payload)
                except Exception as e:
                    logger.warning(f"[SOCKET ERROR] User {user_id}: {str(e)}")

    def notify_user_sync(self, user_id: str, payload: dict, event_type: str = "notification"):
        """
        Synchronous caller to dispatch notification payload if event loop is running.
        """
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                loop.create_task(self.notify_user(user_id, payload, event_type=event_type))
        except RuntimeError:
            pass

    # =========================================================
    # DOMAIN EVENT EMITTERS FOR REAL-TIME UPDATES
    # =========================================================

    def emit_driver_assigned(self, driver_id: str, assignment_data: dict):
        """Realtime update when bike is assigned to driver."""
        self.notify_user_sync(driver_id, assignment_data, event_type="driver_assigned")

    def emit_owner_approved(self, owner_id: str, profile_data: dict):
        """Realtime update when owner verification is approved by admin."""
        self.notify_user_sync(owner_id, profile_data, event_type="owner_approved")

    def emit_payment_completed(self, driver_id: str, payment_data: dict):
        """Realtime update when payment is completed."""
        self.notify_user_sync(driver_id, payment_data, event_type="payment_completed")

    def emit_booking_accepted(self, driver_id: str, booking_data: dict):
        """Realtime update when owner accepts booking request."""
        self.notify_user_sync(driver_id, booking_data, event_type="booking_accepted")

    def emit_admin_verified_bike(self, owner_id: str, bike_data: dict):
        """Realtime update when admin verifies bike."""
        self.notify_user_sync(owner_id, bike_data, event_type="admin_verified_bike")


# Singleton instance used throughout the system
socket_manager = NotificationSocketManager()
