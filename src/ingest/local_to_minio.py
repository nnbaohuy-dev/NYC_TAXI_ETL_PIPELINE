from src.utils.paths import DATA_DIR
from pathlib import Path
from minio import Minio
from src.utils.get_files import get_new_files, get_local_files
from src.database.connection import get_connection
from dotenv import load_dotenv
from src.utils.logger import get_logger
from src.utils.minio import create_minio_client, verify_object
import os
import psycopg


logger = get_logger("local_to_minio")

load_dotenv()

MINIO_RAW_BUCKET = os.getenv("MINIO_RAW_BUCKET")

def upload_parquet(client: Minio, new_files: list[Path], bucket_name: str, connection: psycopg.Connection):
    query = """
        INSERT INTO metadata.file_log(
            source_file,
            raw_loaded
        )
        VALUES (
            %s,
            TRUE
        )
        ON CONFLICT (source_file)
        DO UPDATE
        SET raw_loaded = EXCLUDED.raw_loaded;
    """

    for file in new_files:
        logger.info(f"Đang tải {file.name} vào bucket {bucket_name}")
        logger.info(f"Dung lượng: {file.stat().st_size:,} bytes")

        client.fput_object(
            bucket_name=bucket_name,
            object_name=file.name,
            file_path=str(file),
            content_type="application/vnd.apache.parquet"
        )

        with connection.cursor() as cursor:
            cursor.execute(query, (file.name,))
            connection.commit()

        logger.info(f"Tải thành công {file.name} vào bucket {bucket_name}")


def local_to_minio():
    local_files = get_local_files(DATA_DIR)

    with get_connection() as connection:
        try:
            new_files = get_new_files(local_files, connection)

            if not new_files:
                logger.info(f"Không phát hiện file mới trong {DATA_DIR}")
                return

            client = create_minio_client()

            upload_parquet(
                client=client,
                new_files=new_files,
                bucket_name=MINIO_RAW_BUCKET,
                connection=connection
            )

        except Exception:
            logger.exception("Lỗi khi tải dữ liệu vào raw")
            raise


if __name__ == "__main__":
    local_to_minio()