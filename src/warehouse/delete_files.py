import psycopg

from src.utils.logger import get_logger

logger = get_logger(__name__)


def delete_files(source_files: list[str], connection: psycopg.Connection):
    for source_file in source_files:
        logger.info(f"Đang xóa file: {source_file}")

        file_name = source_file.removesuffix(".parquet")
        year, month = file_name.split("_")[-1].split("-")
        partition_name = f"fact_trip_{int(year):04d}_{int(month):02d}"

        truncate_partition = psycopg.sql.SQL(
            """
            TRUNCATE TABLE warehouse.{partition_name}
            """
        ).format(
            partition_name=psycopg.sql.Identifier(partition_name)
        )

        update_file_log = """
            UPDATE metadata.file_log
            SET warehouse_loaded = FALSE
            WHERE source_file = %s;
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(truncate_partition)
                logger.info(f"Truncate thành công")
                cursor.execute(update_file_log, (source_file,))
                logger.info(f"Xóa dữ liệu {source_file}")

        except Exception:
            logger.exception("Lỗi")
            raise