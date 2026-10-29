from minio import Minio
from dotenv import load_dotenv
from src.utils.logger import get_logger
from src.utils.minio import create_minio_client, verify_object
from src.utils.schema import COLUMN_MAPPING
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

load_dotenv()

def transform(df: DataFrame, source_file: str) -> DataFrame:

    # Rename columns
    for old_name, new_name in COLUMN_MAPPING.items():
        if old_name in df.columns:
            df = df.withColumnRenamed(old_name, new_name)


    df = df.withColumn(
        "congestion_surcharge",
        F.col("congestion_surcharge").cast("double")
    )
    
    df = df.withColumn(
        "airport_fee",
        F.col("airport_fee").cast("double")
    )

    # Filter invalid records
    df = df.filter(
        (F.col("pickup_datetime").isNotNull())
        & (F.col("dropoff_datetime").isNotNull())
        & (F.col("dropoff_datetime") > F.col("pickup_datetime"))
        & (F.col("passenger_count") > 0)
        & (F.col("trip_distance") > 0)
        & (F.col("ratecode_id").isin(1, 2, 3, 4, 5, 6, 99))
        & (F.col("vendor_id").isin(1, 2, 6, 7))
        & (F.col("payment_type_id").isin(0, 1, 2, 3, 4, 5, 6))
        & (F.col("store_and_fwd_flag").isin("Y", "N"))
    )

    df = df.withColumn(
        "trip_duration",
        F.expr(
            "timestampdiff(SECOND, pickup_datetime, dropoff_datetime)"
        ) / 60.0
    )

    df = df.withColumn(
        "average_speed_mph",
        F.col("trip_distance") / (F.col("trip_duration") / 60.0),
    )

    df = df.filter(
        ~(
            (F.col("trip_duration") >= 4 * 60)
            & (F.col("average_speed_mph") < 1)
        )
    )

    df = df.withColumn(
        "source_file", F.lit(source_file)
    )
    
    return df