# app/notifications/socket_manager.py

import logging
import asyncio
from typing import Dict, Set, Any

logger = logging.getLogger(__name__)


class NotificationSocketManager:
    """
    Manages real-time WebSocket / Socket.IO connections per user_id.
    Broadcasts live notification events.
    """

    def __init__(self):
        self.active_connections: Dict[str, Set[Any]] = {}

    def connect(self, user_id: str, connection: Any):
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(connection)
        logger.info(f"[NOTIFICATION SOCKET] User {user_id} connected to real-time notification stream.")

    def disconnect(self, user_id: str, connection: Any):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(connection)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"[NOTIFICATION SOCKET] User {user_id} disconnected from notification stream.")

    async def notify_user(self, user_id: str, payload: dict):
        """
        Sends notification payload to active user socket sessions.
        """
        if user_id in self.active_connections:
            connections = list(self.active_connections[user_id])
            for conn in connections:
                try:
                    if hasattr(conn, "send_json"):
                        await conn.send_json(payload)
                    elif hasattr(conn, "emit"):
                        await conn.emit("notification", payload)
                except Exception as e:
                    logger.warning(f"[NOTIFICATION SOCKET ERROR] User {user_id}: {str(e)}")

    def notify_user_sync(self, user_id: str, payload: dict):
        """
        Synchronous caller to dispatch notification payload if event loop is running.
        """
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                loop.create_task(self.notify_user(user_id, payload))
        except RuntimeError:
            pass


# Singleton instance used throughout the system
socket_manager = NotificationSocketManager()
