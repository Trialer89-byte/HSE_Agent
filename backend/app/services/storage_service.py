from typing import Optional
import os
from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile, HTTPException, status
import uuid

from app.config.settings import settings


class StorageService:
    """
    Service for MinIO object storage operations
    """
    
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        
        # Ensure bucket exists
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """
        Ensure the default bucket exists
        """
        try:
            if not self.client.bucket_exists(settings.minio_bucket_name):
                self.client.make_bucket(settings.minio_bucket_name)
        except S3Error as e:
            print(f"Error creating bucket: {e}")
    
    async def upload_file(self, file: UploadFile, object_name: str = None) -> str:
        """
        Upload file to MinIO storage
        """
        if not object_name:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            object_name = f"{uuid.uuid4()}{file_extension}"
        
        try:
            # Get file size
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(0)  # Reset to beginning
            
            # Upload file
            self.client.put_object(
                bucket_name=settings.minio_bucket_name,
                object_name=object_name,
                data=file.file,
                length=file_size,
                content_type=file.content_type or "application/octet-stream"
            )
            
            return object_name
            
        except S3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error during upload: {str(e)}"
            )
    
    async def download_file(self, object_name: str) -> bytes:
        """
        Download file from MinIO storage
        """
        try:
            response = self.client.get_object(
                bucket_name=settings.minio_bucket_name,
                object_name=object_name
            )
            
            data = response.read()
            response.close()
            response.release_conn()
            
            return data
            
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to download file: {str(e)}"
            )
    
    async def delete_file(self, object_name: str) -> bool:
        """
        Delete file from MinIO storage
        """
        try:
            self.client.remove_object(
                bucket_name=settings.minio_bucket_name,
                object_name=object_name
            )
            return True
            
        except S3Error as e:
            print(f"Error deleting file {object_name}: {e}")
            return False
    
    def get_file_url(self, object_name: str, expires_in_hours: int = 24) -> str:
        """
        Get presigned URL for file download
        """
        try:
            from datetime import timedelta
            
            url = self.client.presigned_get_object(
                bucket_name=settings.minio_bucket_name,
                object_name=object_name,
                expires=timedelta(hours=expires_in_hours)
            )
            
            return url
            
        except S3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate file URL: {str(e)}"
            )
    
    def list_files(self, prefix: str = "") -> list:
        """
        List files in storage with optional prefix filter
        """
        try:
            objects = self.client.list_objects(
                bucket_name=settings.minio_bucket_name,
                prefix=prefix,
                recursive=True
            )
            
            files = []
            for obj in objects:
                files.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag
                })
            
            return files
            
        except S3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list files: {str(e)}"
            )