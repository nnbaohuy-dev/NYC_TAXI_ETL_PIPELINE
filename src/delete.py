from src.warehouse.delete_files import delete_files
from src.database.connection import get_connection

files = ["yellow_tripdata_2016-01.parquet"]

with get_connection() as connection:
    try:
        delete_files(files, connection)
        connection.commit()

    except:
        connection.rollback()