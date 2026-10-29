from datetime import date

import psycopg
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.utils.logger import get_logger

logger = get_logger("load_date")


def get_date_range(df: DataFrame):
    min_pickup_datetime = (
        df.select(F.min("pickup_datetime").alias("min_pickup_datetime"))
        .first()["min_pickup_datetime"]
    )

    max_dropoff_datetime = (
        df.select(F.max("dropoff_datetime").alias("max_dropoff_datetime"))
        .first()["max_dropoff_datetime"]
    )

    min_pickup_date = min_pickup_datetime.date()
    last_date = max_dropoff_datetime.date()

    first_date = date(
        min_pickup_date.year,
        min_pickup_date.month,
        1
    )

    return first_date, last_date


def load_dim_date(df: DataFrame, connection: psycopg.Connection):
    first_date, last_date = get_date_range(df)

    sql = """
    INSERT INTO warehouse.dim_date
    (
        date_key,
        full_date,
        year,
        quarter,
        month,
        month_name,
        day,
        day_of_week,
        day_name,
        week_of_year,
        is_weekend
    )
    SELECT
        TO_CHAR(calendar_date, 'YYYYMMDD')::INTEGER AS date_key,
        calendar_date AS full_date,
        EXTRACT(YEAR FROM calendar_date)::SMALLINT AS year,
        EXTRACT(QUARTER FROM calendar_date)::SMALLINT AS quarter,
        EXTRACT(MONTH FROM calendar_date)::SMALLINT AS month,
        TO_CHAR(calendar_date, 'FMMonth') AS month_name,
        EXTRACT(DAY FROM calendar_date)::SMALLINT AS day,
        EXTRACT(DOW FROM calendar_date)::SMALLINT AS day_of_week,
        TO_CHAR(calendar_date, 'FMDay') AS day_name,
        EXTRACT(WEEK FROM calendar_date)::SMALLINT AS week_of_year,
        EXTRACT(ISODOW FROM calendar_date) IN (6, 7) AS is_weekend
    FROM generate_series(
        %s::DATE,
        %s::DATE,
        INTERVAL '1 day'
    ) AS calendar_date
    ON CONFLICT (date_key)
    DO NOTHING;
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, (first_date, last_date))

        logger.info(
            f"Cập nhật thành công ngày tháng từ {first_date} đến {last_date}"
        )

    except Exception:
        logger.exception(
            f"Không thể cập nhật ngày tháng từ {first_date} đến {last_date}"
        )
        raise