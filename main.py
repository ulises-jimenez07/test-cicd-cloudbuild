from google.cloud import bigquery
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
big_query_client = bigquery.Client()

# Load configuration from environment variables
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_DATASET = os.getenv("BQ_DATASET")
BQ_TABLE_NAME = os.getenv("BQ_TABLE_NAME")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GCS_CSV_FILE_PATH = os.getenv("GCS_CSV_FILE_PATH")

@app.get("/")
def insert_bigquery():
    table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE_NAME}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
    )
    uri = f"gs://{GCS_BUCKET_NAME}/{GCS_CSV_FILE_PATH}"
    load_job = big_query_client.load_table_from_uri(
        uri, table_id, job_config=job_config
    )

    load_job.result()

    destination_table = big_query_client.get_table(table_id)
    return JSONResponse({"data": destination_table.num_rows})
