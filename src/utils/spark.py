from pyspark.sql import SparkSession
from dotenv import load_dotenv
import os

load_dotenv()

def create_sparksession(app_name: str) -> SparkSession:
    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")

    spark = (
        SparkSession.builder
        .appName(app_name)

        .config(
            "spark.hadoop.fs.s3a.endpoint",
            f"http://minio:9000",
        )
        .config(
            "spark.hadoop.fs.s3a.access.key",
            access_key,
        )
        .config(
            "spark.hadoop.fs.s3a.secret.key",
            secret_key,
        )
        .config(
            "spark.hadoop.fs.s3a.path.style.access",
            "true",
        )
        .config(
            "spark.hadoop.fs.s3a.connection.ssl.enabled",
            "false",
        )

        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    return spark