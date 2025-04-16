"""
ETL Pipeline for Retail Sales Data Analysis
This DAG implements an ETL pipeline that extracts sales data from PostgreSQL and a CSV file,
transforms the data by cleaning and aggregating it, and loads it into a MySQL data warehouse.
"""

from datetime import datetime, timedelta
import pandas as pd
import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mysql.hooks.mysql import MySqlHook

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 3, 1),
}

# DAG definition
dag = DAG(
    'retail_sales_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for retail sales data analysis',
    schedule_interval='@daily',
    catchup=False,
)

# Define the path for the CSV file (you might need to adjust this)
CSV_FILE_PATH = 'in_store_sales.csv'

# Define the SQL for creating MySQL table (if it doesn't exist)
create_mysql_table_sql = """
CREATE TABLE IF NOT EXISTS aggregated_sales (
    product_id INT PRIMARY KEY,
    total_quantity INT,
    total_sale_amount DECIMAL(12, 2)
);
"""

# Function to extract data from PostgreSQL
def extract_postgres_data():
    postgres_hook = PostgresHook(postgres_conn_id="postgres_conn")
    
    # SQL query to extract online sales data
    sql_query = """
    SELECT product_id, quantity, sale_amount, sale_date
    FROM online_sales
    WHERE sale_date = %s
    """
    
    # Get yesterday's date (or adjust based on your requirements)
    execution_date = "{{ ds }}"
    
    # Execute the query and fetch the data
    df = postgres_hook.get_pandas_df(sql_query, parameters=(execution_date,))
    
    # Save the data to a temporary CSV file for later processing
    temp_file_path = f"/tmp/postgres_data_{execution_date}.csv"
    df.to_csv(temp_file_path, index=False)
    
    return temp_file_path

# Function to extract data from CSV
def extract_csv_data():
    # Get yesterday's date (or adjust based on your requirements)
    execution_date = "{{ ds }}"
    
    # Read the CSV file
    df = pd.read_csv(CSV_FILE_PATH)
    
    # Filter for the relevant date
    df = df[df['sale_date'] == execution_date]
    
    # Save the filtered data to a temporary CSV file
    temp_file_path = f"/tmp/csv_data_{execution_date}.csv"
    df.to_csv(temp_file_path, index=False)
    
    return temp_file_path

# Function to transform the data
def transform_data(**kwargs):
    # Get the file paths from XCom
    ti = kwargs['ti']
    postgres_file = ti.xcom_pull(task_ids='extract_postgres_data')
    csv_file = ti.xcom_pull(task_ids='extract_csv_data')
    
    # Read the data from the temporary files
    df_postgres = pd.read_csv(postgres_file)
    df_csv = pd.read_csv(csv_file)
    
    # Combine the data from both sources
    df_combined = pd.concat([df_postgres, df_csv], ignore_index=True)
    
    # Data cleansing - remove null or invalid entries
    df_combined = df_combined.dropna()
    
    # Ensure numeric types
    df_combined['quantity'] = pd.to_numeric(df_combined['quantity'], errors='coerce')
    df_combined['sale_amount'] = pd.to_numeric(df_combined['sale_amount'], errors='coerce')
    df_combined = df_combined.dropna()
    
    # Aggregate the data to calculate totals for each product_id
    df_aggregated = df_combined.groupby('product_id').agg({
        'quantity': 'sum',
        'sale_amount': 'sum'
    }).reset_index()
    
    # Rename columns to match the target schema
    df_aggregated.columns = ['product_id', 'total_quantity', 'total_sale_amount']
    
    # Save the transformed data
    transformed_file_path = f"/tmp/transformed_data_{kwargs['ds']}.csv"
    df_aggregated.to_csv(transformed_file_path, index=False)
    
    return transformed_file_path

# Function to load data to MySQL
def load_to_mysql(**kwargs):
    # Get the transformed data file path from XCom
    ti = kwargs['ti']
    transformed_file = ti.xcom_pull(task_ids='transform_data')
    
    # Read the transformed data
    df = pd.read_csv(transformed_file)
    
    # Connect to MySQL using the hook
    mysql_hook = MySqlHook(mysql_conn_id="mysql_conn")
    
    # First, delete existing data for these products to avoid duplicates
    # We could use REPLACE or ON DUPLICATE KEY UPDATE in a production scenario
    product_ids = ','.join(str(pid) for pid in df['product_id'].tolist())
    if product_ids:
        mysql_hook.run(f"DELETE FROM aggregated_sales WHERE product_id IN ({product_ids})")
    
    # Insert the aggregated data
    # Prepare the data for insertion
    rows = []
    for _, row in df.iterrows():
        rows.append((
            int(row['product_id']),
            int(row['total_quantity']),
            float(row['total_sale_amount'])
        ))
    
    # Insert the data into MySQL
    mysql_hook.insert_rows(
        table='aggregated_sales',
        rows=rows,
        target_fields=['product_id', 'total_quantity', 'total_sale_amount']
    )
    
    # Clean up temporary files
    os.remove(transformed_file)
    for file_path in ti.xcom_pull(task_ids='extract_postgres_data', include_prior_dates=False):
        if os.path.exists(file_path):
            os.remove(file_path)
    for file_path in ti.xcom_pull(task_ids='extract_csv_data', include_prior_dates=False):
        if os.path.exists(file_path):
            os.remove(file_path)
    
    return True

# Task to create the MySQL table if it doesn't exist
create_mysql_table_task = MySqlOperator(
    task_id='create_mysql_table',
    mysql_conn_id='mysql_conn',
    sql=create_mysql_table_sql,
    dag=dag,
)

# Task to extract data from PostgreSQL
extract_postgres_task = PythonOperator(
    task_id='extract_postgres_data',
    python_callable=extract_postgres_data,
    dag=dag,
)

# Task to extract data from CSV
extract_csv_task = PythonOperator(
    task_id='extract_csv_data',
    python_callable=extract_csv_data,
    dag=dag,
)

# Task to transform the data
transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

# Task to load data to MySQL
load_task = PythonOperator(
    task_id='load_to_mysql',
    python_callable=load_to_mysql,
    provide_context=True,
    dag=dag,
)

# Define task dependencies
create_mysql_table_task >> [extract_postgres_task, extract_csv_task] >> transform_task >> load_task 