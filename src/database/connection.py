import os
import psycopg

from dotenv import load_dotenv

load_dotenv()

POSTGRES_DNS = (
    f"dbname={os.getenv('DB_NAME')} "
    f"user={os.getenv('DB_USER')} "
    f"password={os.getenv('DB_PASSWORD')} "
    f"host=postgres " 
    f"port=5432 "
)

SPARK_TO_POSTGRES = (
    f"dbname={os.getenv('POSTGRES_DB')} "
    f"user={os.getenv('POSTGRES_USER')} "
    f"password={os.getenv('POSTGRES_PASSWORD')} "
    f"host={os.getenv('POSTGRES_HOST')} "
    f"port={os.getenv('POSTGRES_PORT')} "
)

def get_connection():
    return psycopg.connect(
        POSTGRES_DNS,
        autocommit=False
    )

def spark_to_postgresql():
     return psycopg.connect(
            SPARK_TO_POSTGRES,
            autocommit=False
        )