# ETL-Microservices-Retail: ETL Pipeline

This project implements an ETL (Extract, Transform, Load) pipeline for retail sales data analysis. It extracts data from PostgreSQL (online sales) and CSV files (in-store sales), transforms the data, and loads it into a MySQL data warehouse.

## Project Structure

```
├── README.md                    # Main project documentation
├── airflow_etl_documentation.md # Detailed ETL documentation
├── dag_visualization.png        # DAG visualization
├── etl_pipeline.py              # Standalone ETL script
├── etl_pipeline_dag.py          # Airflow DAG definition
├── in_store_sales.csv           # Sample in-store sales data
├── requirements.txt             # Project dependencies
├── setup_mysql.sql              # MySQL setup script
└── setup_postgres.sql           # PostgreSQL setup script
```

## Requirements

- Python 3.10+
- PostgreSQL
- MySQL
- Python packages: 
  - apache-airflow==2.7.1
  - apache-airflow-providers-postgres==5.7.0
  - apache-airflow-providers-mysql==5.3.0
  - pandas==2.1.0
  - psycopg2-binary==2.9.7
  - mysql-connector-python==8.1.0
  - networkx
  - matplotlib

## Setup Instructions

### 1. Install Required Packages

```bash
pip install -r requirements.txt
```

### 2. Database Setup

#### PostgreSQL Setup

```bash
psql -U postgres -c "CREATE DATABASE retail;"
psql -U postgres -d retail -f setup_postgres.sql
```

This creates a PostgreSQL database named 'retail' and populates it with sample data.

#### MySQL Setup

```bash
mysql -u root -p < setup_mysql.sql
```

This creates a MySQL database named 'retail_dw' with a table for aggregated sales data.

### 3. Running the ETL Pipeline

#### Option 1: Standalone Python Script

To run the ETL pipeline directly:

```bash
python etl_pipeline.py
```

#### Option 2: Airflow DAG

For production environments, you can set up Apache Airflow to run the ETL pipeline on a schedule:

1. Install Apache Airflow following the [official installation guide](https://airflow.apache.org/docs/apache-airflow/stable/installation/index.html)

2. Copy the `etl_pipeline_dag.py` file to your Airflow DAGs directory

3. Set up the database connections in Airflow UI:
   - postgres_conn: Connection to PostgreSQL
   - mysql_conn: Connection to MySQL

4. Start the Airflow webserver and scheduler

5. Access the Airflow web UI and enable the DAG

6. The pipeline will now run according to the schedule (daily by default)

### 4. Verifying Results

After running the ETL pipeline, verify the results by checking the MySQL database:

```sql
SELECT * FROM aggregated_sales;
```

This should show the aggregated sales data with calculated totals for each product.

## Project Documentation

- [Detailed ETL Documentation](airflow_etl_documentation.md): Comprehensive explanation of the ETL pipeline implementation with Apache Airflow

## Key Features

1. **Data Integration**: Combines data from multiple sources (PostgreSQL and CSV)
2. **Data Transformation**: Cleans and aggregates data
3. **Airflow Workflow**: Uses Apache Airflow for task orchestration
4. **Parallel Processing**: Extracts data from sources concurrently
5. **Error Handling**: Handles data inconsistencies and ensures data integrity

## License

This project is available under the MIT License. 