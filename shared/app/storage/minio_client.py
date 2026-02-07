"""MinIO client for media storage"""
from minio import Minio
from minio.error import S3Error
import os
import io
import uuid
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


class MediaStorage:
    """MediaStorage handles file uploads/downloads to MinIO object storage"""
    
    def __init__(self):
        endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        access_key = os.getenv("MINIO_ROOT_USER", "historian")
        secret_key = os.getenv("MINIO_ROOT_PASSWORD", "historian123")
        
        logger.info(f"Initializing MinIO client with endpoint: {endpoint}")
        
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False  # Internal Docker network, no TLS
        )
        self.bucket = os.getenv("MINIO_BUCKET", "matrix-media")
        self._ensure_bucket()
        # Public-facing MinIO client for presigned URLs
        public_url = os.getenv("MINIO_PUBLIC_URL")
        if public_url:
            from urllib.parse import urlparse
            parsed = urlparse(public_url)
            public_endpoint = parsed.netloc or parsed.path
            public_secure = parsed.scheme == "https"
            self.public_client = Minio(
                public_endpoint,
                access_key=access_key,
                ecret_key=secret_key,
                secure=public_secure,
            )
        else:
            self.public_client = self.client
    
    def _ensure_bucket(self):
        """Ensure the bucket exists, create if it doesn't"""
        try:
            if not self.client.bucket_exists(self.bucket):
                logger.info(f"Creating bucket: {self.bucket}")
                self.client.make_bucket(self.bucket)
                logger.info(f"Bucket {self.bucket} created successfully")
            else:
                logger.debug(f"Bucket {self.bucket} already exists")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    def upload(self, data: bytes, filename: str, mime_type: str = "application/octet-stream") -> str:
        """
        Upload file to MinIO
        
        Args:
            data: File data as bytes
            filename: Original filename
            mime_type: MIME type of the file
            
        Returns:
            The MinIO object key
        """
        try:
            # Generate a unique key: UUID/filename
            key = f"{uuid.uuid4()}/{filename}"
            
            logger.info(f"Uploading {len(data)} bytes to {self.bucket}/{key}")
            
            self.client.put_object(
                self.bucket,
                key,
                io.BytesIO(data),
                len(data),
                content_type=mime_type
            )
            
            logger.info(f"Successfully uploaded to {key}")
            return key
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    def download(self, key: str) -> bytes:
        """
        Download file from MinIO
        
        Args:
            key: The MinIO object key
            
        Returns:
            File data as bytes
        """
        try:
            logger.debug(f"Downloading {key} from {self.bucket}")
            response = self.client.get_object(self.bucket, key)
            data = response.read()
            response.close()
            response.release_conn()
            logger.debug(f"Downloaded {len(data)} bytes")
            return data
        except S3Error as e:
            logger.error(f"Error downloading file: {e}")
            raise
    
    def get_url(self, key: str, expires: int = 3600) -> str:
        """
        Get a presigned URL for downloading the file
        
        Args:
            key: The MinIO object key
            expires: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL
        """
        try:
            url = self.public_client.presigned_get_object(
                self.bucket,
                key,
                expires=timedelta(seconds=expires)
            )
            logger.debug(f"Generated presigned URL for {key}")
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
    
    def delete(self, key: str):
        """
        Delete file from MinIO
        
        Args:
            key: The MinIO object key
        """
        try:
            logger.info(f"Deleting {key} from {self.bucket}")
            self.client.remove_object(self.bucket, key)
            logger.info(f"Successfully deleted {key}")
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            raise
    
    def exists(self, key: str) -> bool:
        """
        Check if a file exists in MinIO
        
        Args:
            key: The MinIO object key
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.stat_object(self.bucket, key)
            return True
        except S3Error:
            return False
