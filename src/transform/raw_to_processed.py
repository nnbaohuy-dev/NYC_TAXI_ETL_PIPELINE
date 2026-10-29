from src.transform.transform import transform
from src.utils.get_files import get_metadata_files
from src.database.connection import spark_to_postgresql
from src.utils.spark import create_sparksession
from src.utils.logger import get_logger
from src.transform.validate_schema import validate_schema
import os
from dotenv import load_dotenv

load_dotenv()

MINIO_RAW_BUCKET = os.getenv("MINIO_RAW_BUCKET")
MINIO_PROCESSED_BUCKET = os.getenv("MINIO_PROCESSED_BUCKET")

logger = get_logger("raw_to_processed")


def raw_to_processed():
    spark = create_sparksession("raw_to_processed")
    logger.info("Tạo spark session")
    try:
        with spark_to_postgresql() as connection:
            try:
                raw_done = get_metadata_files(connection, "raw", True)
                processed_done = get_metadata_files(connection, "processed", True)                

                new_files = sorted(raw_done - processed_done)

                for source_file in new_files:
                    raw_path = f"s3a://{MINIO_RAW_BUCKET}/{source_file}"
                    processed_path = f"s3a://{MINIO_PROCESSED_BUCKET}"

                    df = spark.read.parquet(raw_path)

                    df_transformed = transform(df, source_file)

                    if validate_schema(df_transformed):
                        df_transformed.write.format("delta").mode("overwrite").option("replaceWhere", f"source_file = '{source_file}'").save(processed_path)

                        query = """
                            UPDATE metadata.file_log
                            SET processed_loaded = TRUE,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE source_file = %s
                        """
                        with connection.cursor() as cursor:
                            cursor.execute(query, (source_file,))
                            connection.commit()

                        logger.info(f"Tải thành công {source_file} vào bucket processed")

                    else:
                        raise
                    
            except Exception:
                logger.exception("Lỗi khi tải dữ liệu vào processed")
                raise

    finally:
        spark.stop()
        logger.info("Đóng spark session")


if __name__ == "__main__":
    raw_to_processed()