"""
ETL Pipeline for Retail Sales Data Analysis
This script implements an ETL pipeline that extracts sales data from PostgreSQL and a CSV file,
transforms the data by cleaning and aggregating it, and loads it into a MySQL data warehouse.
"""

import pandas as pd
import psycopg2
import mysql.connector
from datetime import datetime

def extract_postgres_data(execution_date=None):
    """Extract data from PostgreSQL database"""
    print("Extracting data from PostgreSQL...")
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host="localhost",
        database="retail",
        user="postgres",
        password="198277"  
    )
    
    # Prepare query
    if execution_date:
        query = f"SELECT product_id, quantity, sale_amount, sale_date FROM online_sales WHERE sale_date = '{execution_date}'"
    else:
        query = "SELECT product_id, quantity, sale_amount, sale_date FROM online_sales"
    
    # Execute query and fetch data
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"Extracted {len(df)} rows from PostgreSQL")
    return df

def extract_csv_data(csv_path, execution_date=None):
    """Extract data from CSV file"""
    print(f"Extracting data from CSV: {csv_path}")
    
    # Read CSV file
    df = pd.read_csv(csv_path)
    
    # Filter by date if provided
    if execution_date:
        df = df[df['sale_date'] == execution_date]
    
    print(f"Extracted {len(df)} rows from CSV")
    return df

def transform_data(postgres_df, csv_df):
    """Transform and aggregate the data"""
    print("Transforming data...")
    
    # Combine data from both sources
    df_combined = pd.concat([postgres_df, csv_df], ignore_index=True)
    
    # Data cleansing - remove null or invalid entries
    df_combined = df_combined.dropna()
    
    # Ensure numeric types
    df_combined['quantity'] = pd.to_numeric(df_combined['quantity'], errors='coerce')
    df_combined['sale_amount'] = pd.to_numeric(df_combined['sale_amount'], errors='coerce')
    df_combined = df_combined.dropna()
    
    # Aggregate data to calculate totals for each product_id
    df_aggregated = df_combined.groupby('product_id').agg({
        'quantity': 'sum',
        'sale_amount': 'sum'
    }).reset_index()
    
    # Rename columns to match the target schema
    df_aggregated.columns = ['product_id', 'total_quantity', 'total_sale_amount']
    
    print(f"Transformed data to {len(df_aggregated)} aggregated rows")
    return df_aggregated

def load_to_mysql(df_aggregated):
    """Load data to MySQL"""
    print("Loading data to MySQL...")
    
    # Connect to MySQL
    conn = mysql.connector.connect(
        host="localhost",
        database="retail_dw",
        user="mysql",
        password="mysql"
    )
    cursor = conn.cursor()
    
    # Get list of product IDs
    product_ids = df_aggregated['product_id'].tolist()
    product_ids_str = ', '.join(str(id) for id in product_ids)
    
    # Delete existing records for these products
    if product_ids:
        delete_query = f"DELETE FROM aggregated_sales WHERE product_id IN ({product_ids_str})"
        cursor.execute(delete_query)
    
    # Insert the aggregated data
    insert_query = """
    INSERT INTO aggregated_sales (product_id, total_quantity, total_sale_amount)
    VALUES (%s, %s, %s)
    """
    
    # Prepare the data for insertion
    data = [
        (int(row['product_id']), int(row['total_quantity']), float(row['total_sale_amount']))
        for _, row in df_aggregated.iterrows()
    ]
    
    # Execute insert
    cursor.executemany(insert_query, data)
    conn.commit()
    
    print(f"Inserted {len(data)} rows into MySQL")
    
    # Close connection
    cursor.close()
    conn.close()

def run_etl_pipeline(csv_path, execution_date=None):
    """Run the complete ETL pipeline"""
    print(f"Starting ETL pipeline at {datetime.now()}")
    print(f"Processing date: {execution_date if execution_date else 'all dates'}")
    
    # Extract
    postgres_data = extract_postgres_data(execution_date)
    csv_data = extract_csv_data(csv_path, execution_date)
    
    # Transform
    transformed_data = transform_data(postgres_data, csv_data)
    
    # Load
    load_to_mysql(transformed_data)
    
    print(f"ETL pipeline completed at {datetime.now()}")

if __name__ == "__main__":
    # Set the path to your CSV file
    CSV_FILE_PATH = "in_store_sales.csv"
    
    # Run the pipeline for all dates
    # Alternatively, you can specify a date: run_etl_pipeline(CSV_FILE_PATH, "2024-03-01")
    run_etl_pipeline(CSV_FILE_PATH) 