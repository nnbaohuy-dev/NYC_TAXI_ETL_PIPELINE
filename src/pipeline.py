from utils.get_files import get_new_file
from transforrm.raw_to_processed import clean_and_transform_file
from src.transforrm.validate_schema import validate_schema
from src.warehouse.load_dim_date import load_dim_date
from warehouse.processed_to_staging import prepare_fact_trip, load_fact_trip, insert_filename
from src.database.connection import get_connection
from src.utils.logger import get_logger
from src.utils.paths import DATA_DIR
from src.utils.schema import COLUMN_MAPPING

import polars as pl
import csv

logger = get_logger("pipeline")

with get_connection() as connection:
    try:
        files = get_new_file(DATA_DIR, connection)

        for file in files:
            logger.info(f"Bắt đầu xử lý {file.name}")
            df = pl.read_parquet(file)
            df = df.rename(COLUMN_MAPPING)

            if validate_schema(df):
                df = clean_and_transform_file(df)

                load_dim_date(df, connection)

                df = prepare_fact_trip(df, file)
                load_fact_trip(df, connection)
                insert_filename(file.name, connection)

                connection.commit()

                logger.info(f"Hoàn thành xử lý {file.name}")

            else:
                logger.info("Pipeline dừng do thay đổi schema.")
                break

    except Exception:
        connection.rollback()
        logger.exception(f"Lỗi khi chạy pipeline.")