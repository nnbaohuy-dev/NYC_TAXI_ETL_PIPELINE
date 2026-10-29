from datetime import datetime, date
from pyspark.sql import DataFrame, functions as F
from pathlib import Path
import psycopg

from src.utils.schema import FACT_TRIP_COLUMNS
from src.utils.logger import get_logger

logger = get_logger("processed_to_staging")

def prepare_fact_trip(df: DataFrame) -> DataFrame:
    df = df.withColumn(
        "pickup_date_key", F.date_format(F.col("pickup_datetime"), "yyyyMMdd").cast("int")
    )

    df = df.withColumn(
        "dropoff_date_key", F.date_format(F.col("dropoff_datetime"), "yyyyMMdd").cast("int")
    )

    df = df.withColumn(
        "load_timestamp", F.current_timestamp()
    )

    return df.select(*FACT_TRIP_COLUMNS)


def load_staging(df: DataFrame, connection: psycopg.Connection, jdbc_url: str, jdbc_properties: dict):
    logger.info(
        f"Ghi dữ liệu vào warehouse.staging"
    )

    query = """
        TRUNCATE TABLE warehouse.staging CASCADE 
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        connection.commit()

    df.write.mode("append").jdbc(
        url=jdbc_url,
        table="warehouse.staging",
        properties=jdbc_properties,
    )

    logger.info(
        f"Load dữ liệu vào warehouse.staging thành công"
    )


def validate_data(df: DataFrame, connection: psycopg.Connection) -> bool:
    try:
        query = """
            SELECT COUNT(*)
            FROM warehouse.staging
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            staging_rows = cursor.fetchone()[0]

        file_rows = df.count()

        logger.info(
            f"Validation staging: file = {file_rows}, PostgreSQL = {staging_rows}"
        )

        if file_rows == staging_rows:
            return True

        else:
            truncate_query = """
                TRUNCATE TABLE warehouse.staging CASCADE
            """

            logger.error(
                "Số dòng không khớp"
            )

            try:
                with connection.cursor() as cursor:
                    cursor.execute(truncate_query)
                    return False
                
            except Exception:
                logger.exception("Lỗi khi truncate staging")
                raise

    except Exception:
        logger.exception("Lỗi khi validate warehouse.staging")
        raise