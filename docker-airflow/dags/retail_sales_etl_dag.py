"""
Retail Sales ETL DAG

This DAG orchestrates the retail sales ETL pipeline, which:
1. Extracts data from PostgreSQL database and CSV files
2. Transforms the data (cleaning and aggregation)
3. Loads the transformed data into a MySQL data warehouse
"""

import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Import the ETL functions
import sys
sys.path.append('/opt/airflow/retail_sales_etl')
from etl_pipeline import extract_postgres_data, extract_csv_data, transform_data, load_to_mysql

# Define default arguments
default_args = {
    'owner': 'Abdullah Mahmoud',
    'depends_on_past': False,
    'email': ['abdullah20032003@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1),
}

# Define the DAG
dag = DAG(
    'retail_sales_etl',
    default_args=default_args,
    description='ETL pipeline for retail sales data',
    schedule_interval='@daily',
    catchup=False,
)

# Define the path to the CSV file
csv_file_path = '/opt/airflow/retail_sales_etl/in_store_sales.csv'

# Define the extract task from PostgreSQL
def extract_postgres_wrapper(**kwargs):
    execution_date = kwargs.get('ds')
    df = extract_postgres_data(execution_date)
    return df.to_json()

extract_postgres_task = PythonOperator(
    task_id='extract_postgres_data',
    python_callable=extract_postgres_wrapper,
    provide_context=True,
    dag=dag,
)

# Define the extract task from CSV
def extract_csv_wrapper(**kwargs):
    execution_date = kwargs.get('ds')
    df = extract_csv_data(csv_file_path, execution_date)
    return df.to_json()

extract_csv_task = PythonOperator(
    task_id='extract_csv_data',
    python_callable=extract_csv_wrapper,
    provide_context=True,
    dag=dag,
)

# Define the transform task
def transform_data_wrapper(**kwargs):
    # Get XComs from upstream tasks
    ti = kwargs['ti']
    postgres_data_json = ti.xcom_pull(task_ids='extract_postgres_data')
    csv_data_json = ti.xcom_pull(task_ids='extract_csv_data')
    
    # Convert JSON back to DataFrame
    import pandas as pd
    postgres_data = pd.read_json(postgres_data_json)
    csv_data = pd.read_json(csv_data_json)
    
    # Transform the data
    transformed_df = transform_data(postgres_data, csv_data)
    return transformed_df.to_json()

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data_wrapper,
    provide_context=True,
    dag=dag,
)

# Define the load task
def load_data_wrapper(**kwargs):
    # Get XCom from transform task
    ti = kwargs['ti']
    transformed_data_json = ti.xcom_pull(task_ids='transform_data')
    
    # Convert JSON back to DataFrame
    import pandas as pd
    transformed_df = pd.read_json(transformed_data_json)
    
    # Load the data
    load_to_mysql(transformed_df)

load_task = PythonOperator(
    task_id='load_to_mysql',
    python_callable=load_data_wrapper,
    provide_context=True,
    dag=dag,
)

# Define the task dependencies
[extract_postgres_task, extract_csv_task] >> transform_task >> load_task 