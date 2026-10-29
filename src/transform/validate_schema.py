'''
from pyspark.sql import DataFrame

from src.utils.schema import EXPECTED_SCHEMA
from src.utils.logger import get_logger

logger = get_logger(__name__)

def validate_schema(df: DataFrame) -> bool:
    schema = {}

    for column, dtype in df.schema.items():
        if str(dtype).startswith("Datetime"):
            schema[column] = "Datetime"
        else:
            schema[column] = str(dtype)

    match = schema == EXPECTED_SCHEMA

    if not match:
        match = False
        logger.error(f"Có thay đổi schema")

        added_columns  = sorted(set(schema) - set(EXPECTED_SCHEMA))
        if added_columns:
            logger.error(f"Thay đổi schema, thêm các cột: {added_columns}")

        removed_columns  = sorted(set(EXPECTED_SCHEMA) - set(schema))
        if removed_columns:
            logger.error(f"Thay đổi schema, loại bỏ các cột: {removed_columns}")

        changed_dtype = []

        for column in EXPECTED_SCHEMA:
            if column not in schema:
                continue

            else:
                if EXPECTED_SCHEMA[column] != schema[column]:
                    changed_dtype.append(column)
        if changed_dtype:
            logger.error(f"Thay đổi schema, kiểu dữ liệu thay đổi: {changed_dtype}")

    return match
'''

#Spark version

from collections import Counter

from pyspark.sql import DataFrame

from src.utils.schema import EXPECTED_SCHEMA_SPK_V
from src.utils.logger import get_logger

logger = get_logger("Schema validation")


def validate_schema(df: DataFrame) -> bool:
    schema = {
        field.name: field.dataType.simpleString()
        for field in df.schema.fields
    }

    expected = EXPECTED_SCHEMA_SPK_V

    column_names = [field.name for field in df.schema.fields]
    duplicates = sorted(
        name
        for name, count in Counter(column_names).items()
        if count > 1
    )

    if duplicates:
        logger.error(f"Duplicate columns detected: {duplicates}")
        return False

    added_columns = sorted(set(schema) - set(expected))
    removed_columns = sorted(set(expected) - set(schema))

    changed_dtype = {
        column: {
            "expected": expected[column],
            "actual": schema[column],
        }
        for column in expected.keys() & schema.keys()
        if expected[column] != schema[column]
    }

    if added_columns or removed_columns or changed_dtype:
        logger.error("Schema validation failed")

        if added_columns:
            logger.error(f"Added columns: {added_columns}")

        if removed_columns:
            logger.error(f"Missing columns: {removed_columns}")

        if changed_dtype:
            logger.error(f"Changed data types: {changed_dtype}")

        return False

    logger.info("Schema validation passed")
    return True
