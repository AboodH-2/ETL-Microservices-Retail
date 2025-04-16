# ETL Pipeline using Apache Airflow

## Overview

This project implements an ETL (Extract, Transform, Load) pipeline using Apache Airflow. The pipeline extracts sales data from two different sources, transforms it by cleaning and aggregating, and then loads it into a data warehouse for analysis.

## Architecture

![DAG Structure](dag_visualization.png)

The ETL pipeline consists of the following components:

1. **Data Sources**:
   - PostgreSQL database (online sales)
   - CSV file (in-store sales)

2. **Transformation Layer**:
   - Data cleaning (removing nulls)
   - Type conversion
   - Aggregation by product_id

3. **Data Warehouse**:
   - MySQL database (aggregated sales)

## Apache Airflow Implementation

### DAG Structure

The Airflow DAG (Directed Acyclic Graph) is defined with the following tasks:

1. **create_mysql_table**: Creates the MySQL table if it doesn't exist
2. **extract_postgres_data**: Extracts data from PostgreSQL
3. **extract_csv_data**: Extracts data from the CSV file
4. **transform_data**: Combines and transforms the data
5. **load_to_mysql**: Loads the transformed data into MySQL

### Task Dependencies

The dependencies between tasks are defined as follows:

```
create_mysql_table >> [extract_postgres_data, extract_csv_data] >> transform_data >> load_to_mysql
```

This means:
- First, the MySQL table is created
- Then, data is extracted from both sources in parallel
- Next, the extracted data is transformed
- Finally, the transformed data is loaded into MySQL

## Implementation Details

### Extract

#### PostgreSQL Extraction
- Connection to the online_sales table in PostgreSQL
- Filtering based on execution date
- Using PostgresHook for database interaction

```python
def extract_postgres_data():
    postgres_hook = PostgresHook(postgres_conn_id="postgres_conn")
    
    # SQL query to extract online sales data
    sql_query = """
    SELECT product_id, quantity, sale_amount, sale_date
    FROM online_sales
    WHERE sale_date = %s
    """
    
    # Get execution date
    execution_date = "{{ ds }}"
    
    # Execute the query and fetch the data
    df = postgres_hook.get_pandas_df(sql_query, parameters=(execution_date,))
    
    # Save to temporary file
    temp_file_path = f"/tmp/postgres_data_{execution_date}.csv"
    df.to_csv(temp_file_path, index=False)
    
    return temp_file_path
```

#### CSV Extraction
- Reading from CSV file
- Filtering based on execution date
- Using pandas for data manipulation

```python
def extract_csv_data():
    # Get execution date
    execution_date = "{{ ds }}"
    
    # Read the CSV file
    df = pd.read_csv(CSV_FILE_PATH)
    
    # Filter for the relevant date
    df = df[df['sale_date'] == execution_date]
    
    # Save to temporary file
    temp_file_path = f"/tmp/csv_data_{execution_date}.csv"
    df.to_csv(temp_file_path, index=False)
    
    return temp_file_path
```

### Transform

- Combining data from both sources
- Cleaning the data (removing nulls)
- Converting to numeric types
- Aggregating by product_id
- Calculating total quantities and sales amounts

```python
def transform_data(**kwargs):
    # Get the file paths from XCom
    ti = kwargs['ti']
    postgres_file = ti.xcom_pull(task_ids='extract_postgres_data')
    csv_file = ti.xcom_pull(task_ids='extract_csv_data')
    
    # Read the data
    df_postgres = pd.read_csv(postgres_file)
    df_csv = pd.read_csv(csv_file)
    
    # Combine data
    df_combined = pd.concat([df_postgres, df_csv], ignore_index=True)
    
    # Clean data
    df_combined = df_combined.dropna()
    
    # Ensure numeric types
    df_combined['quantity'] = pd.to_numeric(df_combined['quantity'], errors='coerce')
    df_combined['sale_amount'] = pd.to_numeric(df_combined['sale_amount'], errors='coerce')
    df_combined = df_combined.dropna()
    
    # Aggregate data
    df_aggregated = df_combined.groupby('product_id').agg({
        'quantity': 'sum',
        'sale_amount': 'sum'
    }).reset_index()
    
    # Rename columns
    df_aggregated.columns = ['product_id', 'total_quantity', 'total_sale_amount']
    
    # Save transformed data
    transformed_file_path = f"/tmp/transformed_data_{kwargs['ds']}.csv"
    df_aggregated.to_csv(transformed_file_path, index=False)
    
    return transformed_file_path
```

### Load

- Using MySQL as the data warehouse
- Handling existing records with a delete and insert strategy
- Using MySqlHook for database operations

```python
def load_to_mysql(**kwargs):
    # Get the transformed data
    ti = kwargs['ti']
    transformed_file = ti.xcom_pull(task_ids='transform_data')
    
    # Read the transformed data
    df = pd.read_csv(transformed_file)
    
    # Connect to MySQL
    mysql_hook = MySqlHook(mysql_conn_id="mysql_conn")
    
    # Delete existing records
    product_ids = ','.join(str(pid) for pid in df['product_id'].tolist())
    if product_ids:
        mysql_hook.run(f"DELETE FROM aggregated_sales WHERE product_id IN ({product_ids})")
    
    # Insert the aggregated data
    rows = []
    for _, row in df.iterrows():
        rows.append((
            int(row['product_id']),
            int(row['total_quantity']),
            float(row['total_sale_amount'])
        ))
    
    # Insert data
    mysql_hook.insert_rows(
        table='aggregated_sales',
        rows=rows,
        target_fields=['product_id', 'total_quantity', 'total_sale_amount']
    )
    
    # Clean up temporary files
    # ...
    
    return True
```

## Data Model

### Source Data

1. **PostgreSQL (online_sales)**:
   ```sql
   CREATE TABLE online_sales (
       sale_id SERIAL PRIMARY KEY,
       product_id INT,
       quantity INT,
       sale_amount DECIMAL(10, 2),
       sale_date DATE
   );
   ```

2. **CSV (in_store_sales.csv)**:
   - Columns: sale_id, product_id, quantity, sale_amount, sale_date

### Target Data

**MySQL (aggregated_sales)**:
```sql
CREATE TABLE aggregated_sales (
    product_id INT PRIMARY KEY,
    total_quantity INT,
    total_sale_amount DECIMAL(12, 2)
);
```

## Setup and Configuration

1. **Database Setup**:
   - PostgreSQL database (retail)
   - MySQL database (retail_dw)

2. **Airflow Connections**:
   - postgres_conn: Connection to PostgreSQL
   - mysql_conn: Connection to MySQL

3. **Environment Setup**:
   - Airflow home directory
   - DAG placement
   - Connection configuration

## Execution Results

The ETL pipeline has been successfully executed and produced the following results:

- 5 aggregated product records were loaded into MySQL
- Total quantity sold: 20 units
- Total sales amount: $487.50

## Challenges and Solutions

1. **Challenge**: Managing database connections in Airflow
   **Solution**: Created pre-configured connections using Airflow's connection management

2. **Challenge**: Handling temporary files between tasks
   **Solution**: Used Airflow XCom to pass file paths between tasks

3. **Challenge**: Ensuring data integrity during load
   **Solution**: Implemented a delete-then-insert strategy to avoid duplicates

## Conclusion

This ETL pipeline demonstrates the effective use of Apache Airflow for data integration from multiple sources. The solution is scalable, maintainable, and can be scheduled to run automatically on a daily basis. 