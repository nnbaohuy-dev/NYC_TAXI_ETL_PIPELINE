from src.warehouse.processed_to_staging import load_staging, prepare_fact_trip, validate_data
from src.warehouse.staging_to_warehouse import staging_to_fact
from src.warehouse.load_dim_date import load_dim_date
from src.utils.logger import get_logger
from src.database.connection import spark_to_postgresql
from src.utils.spark import create_sparksession
from src.utils.get_files import get_metadata_files
from pyspark.sql import functions as F
from dotenv import load_dotenv
import os

logger = get_logger("processed_to_warehouse")

load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

MINIO_PROCESSED_BUCKET = os.getenv("MINIO_PROCESSED_BUCKET")

jdbc_url = (
    f"jdbc:postgresql://"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

jdbc_properties = {
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "driver": "org.postgresql.Driver",
}

def processed_to_warehouse():
    spark = create_sparksession("processed_to_warehouse")
    logger.info("Tạo spark session")
    try:
        with spark_to_postgresql() as connection:
            try:
                processed_done = get_metadata_files(connection, "processed", True)
                warehouse_done = get_metadata_files(connection, "warehouse", True)

                new_files = sorted(processed_done - warehouse_done)
                source_path = f"s3a://{MINIO_PROCESSED_BUCKET}"
                for source_file in new_files:
                    df = spark.read.format("delta").load(source_path).filter(F.col("source_file") == source_file)
                    df = prepare_fact_trip(df)
                    load_staging(df, connection, jdbc_url, jdbc_properties)
                    if validate_data(df, connection):
                        load_dim_date(df, connection)
                        staging_to_fact(df, connection)
                        query = """
                            UPDATE metadata.file_log
                            SET warehouse_loaded = TRUE,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE source_file = %s
                        """
                        with connection.cursor() as cursor:
                            cursor.execute(query, (source_file,))
                        connection.commit()

                        logger.info(f"Hoàn thành load {source_file} từ processed vào warehouse")

                    else:
                        connection.commit()
                        raise ValueError("Validation test failed")

            except Exception:
                connection.rollback()
                logger.exception(f"Lỗi khi tải dữ liệu vào warehouse")
                raise

    finally:
        spark.stop()
        logger.info("Đóng spark session")

if __name__ == "__main__":
    processed_to_warehouse()