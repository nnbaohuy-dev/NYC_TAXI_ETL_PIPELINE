from pathlib import Path

import psycopg

def get_local_files(directory: Path) -> list[Path]:
    if not directory.exists():
        raise(
            f"Không tồn tại {directory}"
        )

    files = sorted(directory.rglob("*.parquet"))

    if not files:
        raise FileNotFoundError(f"Không tồn tại {directory}")

    return files

def get_metadata_files(connection: psycopg.Connection, stage: str, is_loaded: bool) -> set[str]:
    column_name = f"{stage}_loaded"
    query = psycopg.sql.SQL("""
        SELECT source_file
        FROM metadata.file_log
        WHERE {column_name} = %s
        ORDER BY source_file ASC
    """).format(
        column_name=psycopg.sql.Identifier(column_name)
    )

    with connection.cursor() as cursor:
        cursor.execute(query, (is_loaded,))

        return {
            row[0] for row in cursor.fetchall()
        }

def get_new_files(all_files: list[Path], connection: psycopg.Connection) -> list[Path]:
    loaded_files = get_metadata_files(connection, stage="raw", is_loaded=True)

    files = []

    for file in all_files:
        if file.name not in loaded_files:
            files.append(file)

    return files