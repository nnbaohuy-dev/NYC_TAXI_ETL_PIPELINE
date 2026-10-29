from pathlib import Path
from dotenv import load_dotenv
from src.utils.logger import get_logger
from minio import Minio
from minio.error import S3Error
import os

logger = get_logger(__name__)


load_dotenv(override=True)
#load_dotenv()


MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_SECURE = os.getenv("MINIO_SECURE") == "true"


def create_minio_client() -> Minio:
    client = Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )

    return client


def verify_object(client: Minio, bucket_name: str, object_name, file_size) -> bool:
    try:
        object_stat = client.stat_object(
            bucket_name,
            object_name
        )

        if file_size == object_stat.size:
            return True

        else:
            logger.info(f"Kích thước object không khớp. Yêu cầu RELOAD.")
            client.remove_object(
                bucket_name,
                object_name
            )
            return False

    except S3Error as error:
        if error.code in {"NoSuchKey", "NoSuchObject", "NotFound"}:
            return False

        raise

    except Exception as e:
        logger.exception(f"Lỗi khi kiểm tra object")
        raise

