# app/cron/scheduler.py

import asyncio
import logging
from typing import Optional

from app.db.database import SessionLocal
from app.cron.jobs import run_all_cron_jobs

logger = logging.getLogger(__name__)

_cron_task: Optional[asyncio.Task] = None
_keep_running = False


async def _cron_worker_loop(interval_seconds: int = 60):
    """
    Background worker loop executing scheduled cron jobs periodically.
    """
    logger.info(f"[CRON SCHEDULER STARTED] Worker loop active every {interval_seconds}s.")
    
    while _keep_running:
        try:
            db = SessionLocal()
            try:
                run_all_cron_jobs(db)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"[CRON WORKER ERROR] Failed executing background cron cycle: {str(e)}")

        await asyncio.sleep(interval_seconds)


def start_cron_scheduler(interval_seconds: int = 60):
    """
    Starts background cron worker task inside FastAPI asyncio event loop.
    """
    global _cron_task, _keep_running
    if _cron_task is None or _cron_task.done():
        _keep_running = True
        try:
            loop = asyncio.get_running_loop()
            _cron_task = loop.create_task(_cron_worker_loop(interval_seconds))
            logger.info("[CRON SCHEDULER] Background worker successfully spawned.")
        except RuntimeError:
            logger.warning("[CRON SCHEDULER] Event loop not running. Worker skipped.")


def stop_cron_scheduler():
    """
    Stops background cron worker task during application shutdown.
    """
    global _keep_running
    _keep_running = False
    if _cron_task and not _cron_task.done():
        _cron_task.cancel()
        logger.info("[CRON SCHEDULER] Background worker task cancelled.")
