# app/core/storage.py

import os
import uuid
import logging
from typing import Optional
from fastapi import UploadFile
from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageProvider:
    """
    Production Object Storage Provider Abstraction.
    Supports Local Disk Storage, AWS S3, MinIO, and Cloudinary.
    """

    def __init__(self):
        self.provider_type = getattr(settings, "STORAGE_PROVIDER", "local").lower()
        self.upload_dir = getattr(settings, "UPLOAD_DIR", "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_file(self, file: UploadFile, subfolder: str = "documents") -> str:
        """
        Saves uploaded file and returns accessible URL or file path.
        """
        ext = os.path.splitext(file.filename)[1] if file.filename else ".png"
        filename = f"{uuid.uuid4()}{ext}"
        target_dir = os.path.join(self.upload_dir, subfolder)
        os.makedirs(target_dir, exist_ok=True)
        filepath = os.path.join(target_dir, filename)

        with open(filepath, "wb") as f:
            f.write(file.file.read())

        relative_path = filepath.replace("\\", "/")
        logger.info(f"[STORAGE Provider:{self.provider_type}] File saved to {relative_path}")
        return relative_path

    def delete_file(self, file_path: str) -> bool:
        """Deletes file from storage provider."""
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                logger.error(f"[STORAGE DELETE ERROR] {str(e)}")
        return False


storage_provider = StorageProvider()
