from datetime import date
from pyspark.sql import DataFrame, functions as F

import psycopg

from src.utils.logger import get_logger

logger = get_logger("staging_to_warehouse")

def delete_file(source_file: str, connection: psycopg.Connection):
    delete_query = """
        DELETE FROM warehouse.fact_trip
        WHERE source_file = %s;
    """

    update_query = """
        UPDATE metadata.file_log
        SET warehouse_loaded = FALSE
        WHERE source_file = %s;
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(delete_query, (source_file,))
            cursor.execute(update_query, (source_file,))
            
    except Exception:
        logger.exception("Lỗi khi xóa dòng trong warehouse")
        raise


def get_months(df: DataFrame) -> list[date]:
    rows = (
        df.select(F.date_trunc("month", F.col("pickup_datetime")).alias("month")).distinct().orderBy("month").collect()
    )

    return [
        row["month"].date() for row in rows
    ]


def get_next_month(current_month: date) -> date:
    if current_month.month == 12:
        return date(current_month.year + 1, 1, 1)

    return date(current_month.year, current_month.month + 1, 1)


def get_partition_name(partition_month: date) -> str:
    return f"fact_trip_{partition_month.year:04d}_{partition_month.month:02d}"


def ensure_monthly_partition(partition_month: date, connection: psycopg.Connection):
    partition_name = get_partition_name(partition_month)
    next_month = get_next_month(partition_month)

    check_exist = """
        SELECT EXISTS (
            SELECT 1
            FROM pg_class AS c
            JOIN pg_namespace AS n
            ON n.oid = c.relnamespace
            JOIN pg_inherits AS i
            ON i.inhrelid = c.oid
            JOIN pg_class AS parent
            ON parent.oid = i.inhparent
            JOIN pg_namespace AS parent_schema
            ON parent_schema.oid = parent.relnamespace
            WHERE n.nspname = 'warehouse'
            AND c.relname = %s
            AND c.relispartition
            AND parent_schema.nspname = 'warehouse'
            AND parent.relname = 'fact_trip'
        );
    """

    create_partition = psycopg.sql.SQL("""
        CREATE TABLE warehouse.{partition_name}
        PARTITION OF warehouse.fact_trip
        FOR VALUES FROM ({start}) TO ({end})
    """).format(
        partition_name=psycopg.sql.Identifier(partition_name),
        start=psycopg.sql.Literal(partition_month),
        end=psycopg.sql.Literal(next_month),
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(check_exist, (partition_name,))

            partiton_exists = cursor.fetchone()[0]

            if partiton_exists:
                logger.info(f"warehouse.{partition_name} đã tồn tại")
                return

            else:
                cursor.execute(create_partition)
                logger.info(f"Tạo thành công bảng warehouse.{partition_name}")
    
    except Exception:
        logger.exception(f"Lỗi khi tạo bảng warehouse.{partition_name}")
        raise


def staging_to_fact(df: DataFrame, connection: psycopg.Connection):
    load_query = """
        INSERT INTO warehouse.fact_trip (
            pickup_date_key,
            dropoff_date_key,
            pickup_datetime,
            dropoff_datetime,
            vendor_id,
            ratecode_id,
            pickup_location_id,
            dropoff_location_id,
            payment_type_id,
            passenger_count,
            trip_distance,
            trip_duration,
            average_speed_mph,
            fare_amount,
            extra,
            mta_tax,
            tip_amount,
            tolls_amount,
            improvement_surcharge,
            total_amount,
            congestion_surcharge,
            airport_fee,
            source_file,
            load_timestamp
        )
        SELECT
            pickup_date_key,
            dropoff_date_key,
            pickup_datetime,
            dropoff_datetime,
            vendor_id,
            ratecode_id,
            pickup_location_id,
            dropoff_location_id,
            payment_type_id,
            passenger_count,
            trip_distance,
            trip_duration,
            average_speed_mph,
            fare_amount,
            extra,
            mta_tax,
            tip_amount,
            tolls_amount,
            improvement_surcharge,
            total_amount,
            congestion_surcharge,
            airport_fee,
            source_file,
            current_timestamp
        FROM warehouse.staging;
    """

    get_source_files = """
        SELECT DISTINCT source_file
        FROM warehouse.staging
    """
    months = get_months(df)

    for month in months:
        ensure_monthly_partition(month, connection)

    with connection.cursor() as cursor:
        cursor.execute(get_source_files)
        source_file = cursor.fetchone()[0]

    delete_file(source_file, connection)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(load_query)
            logger.info(f"Load thành công {source_file} từ staging vào warehouse")
            
    except Exception:
        logger.exception("Lỗi khi load fact_trip")
        raise