from airflow.sdk import dag, task
from datetime import timedelta
import pendulum 
from src.ingest.local_to_minio import local_to_minio

default_args = {
    "owner": "data-engineer",
    "retries": 2,
    "retry_delay": timedelta(minutes=5)
}

@dag(
    dag_id="ETL-pipeline",
    description="ETL pipeline for NYC Taxi data",
    default_args=default_args,
    start_date=pendulum.datetime(
        2026, 1, 1,
        tz="Asia/Ho_Chi_Minh",
    ),
    catchup=False,
    max_active_runs=1,
    schedule="*/30 * * * *",
)
def etl_pipeline():
    @task
    def upload_local_to_minio():
        local_to_minio()

    @task.bash
    def upload_raw_to_processed():
        return (
            "docker exec "
            "-w /opt/project "
            "-e PYTHONPATH=/opt/project "
            "spark-master "
            "/opt/spark/bin/spark-submit "
            "--master spark://spark-master:7077 "
            "src/transform/raw_to_processed.py"
        ) 
     
    @task.bash
    def upload_processed_to_warehouse():
        return (
            "docker exec "
            "-w /opt/project "
            "-e PYTHONPATH=/opt/project "
            "spark-master "
            "/opt/spark/bin/spark-submit "
            "--master spark://spark-master:7077 "
            "src/warehouse/processed_to_warehouse.py"
        ) 

    upload_local_to_minio() >> upload_raw_to_processed() >> upload_processed_to_warehouse()

etl_pipeline()