# ETL-Microservices-Retail: Airflow Pipeline Documentation

## Part 1: Technical Documentation

### DAG Design

#### Overview
The `retail_sales_etl` DAG orchestrates an ETL (Extract, Transform, Load) pipeline that processes retail sales data from multiple sources, aggregates it, and loads it into a data warehouse. The DAG is scheduled to run daily and processes the most recent day's data.

#### DAG Structure
The DAG follows a simple ETL pattern with parallel extraction tasks:

```
                  ┌─────────────────┐
                  │extract_postgres_│
                  │     data        │
                  └────────┬────────┘
                           │
                           ▼
┌─────────────────┐    ┌─────────┐    ┌─────────────┐
│  extract_csv_   │───▶│transform│───▶│load_to_mysql│
│     data        │    │  data   │    │             │
└─────────────────┘    └─────────┘    └─────────────┘
```

#### Tasks

1. **extract_postgres_data**: Extracts sales data from PostgreSQL database
2. **extract_csv_data**: Extracts sales data from CSV files
3. **transform_data**: Combines and aggregates data from both sources
4. **load_to_mysql**: Loads transformed data into MySQL data warehouse

#### Configuration

- **Schedule**: Daily (`@daily`)
- **Catchup**: Disabled
- **Retries**: 1 with 5 minutes delay
- **Owner**: Abdullah Mahmoud
- **Email**: abdullah20032003@gmail.com

### Operators Used

#### PythonOperator
All tasks use the `PythonOperator` to execute Python functions:

1. **extract_postgres_wrapper**: 
   - Calls `extract_postgres_data` function
   - Returns data as JSON for XCom

2. **extract_csv_wrapper**:
   - Calls `extract_csv_data` function
   - Returns data as JSON for XCom

3. **transform_data_wrapper**:
   - Retrieves data from upstream tasks using XCom
   - Calls `transform_data` function
   - Returns transformed data as JSON for XCom

4. **load_data_wrapper**:
   - Retrieves transformed data using XCom
   - Calls `load_to_mysql` function

#### Data Flow
Data is passed between tasks using Airflow's XCom, serialized as JSON. This approach:
- Maintains clear separation between tasks
- Allows for task retries/restarts
- Enables tracking of intermediate data

### Implementation Details

#### Database Connections

1. **PostgreSQL (Source):**
   - Host: host.docker.internal
   - Database: retail
   - User: postgres
   - Password: 198277

2. **MySQL (Target):**
   - Host: host.docker.internal
   - Database: retail_dw
   - User: mysql
   - Password: mysql

#### File Paths
- CSV Data: `/opt/airflow/retail_sales_etl/in_store_sales.csv`

### Testing Plan

#### Unit Testing

1. **Extract Functions Testing**:
   - Test extraction with and without date filters
   - Verify column structure of extracted data
   - Test handling of empty sources

2. **Transform Function Testing**:
   - Test data aggregation logic
   - Verify handling of null/invalid values
   - Test with edge cases (empty inputs, large datasets)

3. **Load Function Testing**:
   - Verify correct insertion of data
   - Test update/overwrite behavior
   - Verify error handling for database connection failures

#### DAG Testing

1. **Task Execution Testing**:
   - Test each task individually with test data
   - Verify XCom passing between tasks
   - Check error handling and retry behavior

2. **End-to-End Testing**:
   - Run complete DAG with test data
   - Verify data flows correctly through all tasks
   - Confirm final data in MySQL matches expectations

3. **Scheduled Execution Testing**:
   - Test DAG execution with different execution dates
   - Verify date-based filtering works correctly

#### Monitoring and Validation

1. **Data Validation**:
   - Check row counts at each stage
   - Verify aggregation totals match source data
   - Monitor for data quality issues

2. **Performance Monitoring**:
   - Track task execution times
   - Monitor memory usage
   - Identify bottlenecks in the pipeline

### Deployment

The DAG is deployed using Docker Compose with the following components:
- Airflow Webserver
- Airflow Scheduler
- PostgreSQL database (for Airflow metadata)

The entire setup can be started with:
```bash
docker-compose up -d
```

Access the Airflow UI at: http://localhost:8080
- Username: abdullah
- Password: 19821977

## Part 2: Reflection

### Challenges Encountered and Solutions

#### 1. Airflow Installation and Setup on Windows

**Challenge:** Initial attempts to install and run Airflow natively on Windows encountered multiple issues:
- Missing Unix-specific modules (`pwd` module)
- Daemon process errors
- Issues with symbolic links

**Solution:** 
After multiple troubleshooting attempts, I determined that containerization was the best approach. I chose Docker to isolate the Airflow environment from Windows-specific limitations:
- Created a Docker Compose setup with all necessary Airflow components
- Configured volumes to share DAG files and ETL code with the containers
- Used proper networking to allow container access to host databases

This approach completely resolved the compatibility issues while providing a production-like environment for testing.

#### 2. Data Passing Between Tasks

**Challenge:** Figuring out how to effectively pass data between Airflow tasks was complicated, as each task runs as a separate process.

**Solution:**
I implemented a robust solution using Airflow's XCom mechanism:
- Serialized DataFrame objects to JSON before passing between tasks
- Created wrapper functions around core ETL functions to handle XCom interaction
- Implemented proper error handling for data serialization/deserialization

This approach maintained clean separation between tasks while ensuring reliable data flow through the pipeline.

#### 3. Database Connectivity from Docker

**Challenge:** When running Airflow in Docker, connecting to the PostgreSQL and MySQL databases on the host machine proved challenging.

**Solution:**
I resolved this by:
- Using `host.docker.internal` as the hostname in database connection strings to access the host from containers
- Updating the ETL code to use these Docker-specific connection parameters
- Testing connection settings thoroughly before deploying the full pipeline

This approach allowed the containerized Airflow to communicate seamlessly with host databases.

#### 4. DAG Testing and Debugging

**Challenge:** Testing the DAG without having to wait for scheduled execution was time-consuming.

**Solution:**
I optimized the testing process by:
- Leveraging Airflow's "Trigger DAG" feature to run on-demand
- Using the Airflow UI to inspect task logs and debug issues
- Implementing comprehensive logging in the ETL functions

These practices significantly reduced the debugging cycle time and allowed for rapid iteration.

#### 5. Error Handling and Robustness

**Challenge:** Ensuring the ETL pipeline was robust against various failure scenarios was complex.

**Solution:**
I improved error handling by:
- Adding proper exception handling in critical sections of the code
- Configuring task retries for transient errors
- Implementing data validation at each stage of the pipeline

These measures significantly improved the pipeline's reliability and maintainability.

### Key Learnings

1. **Containerization Benefits:** Docker proved invaluable for creating a consistent environment and bypassing OS-specific limitations.

2. **Airflow Architecture:** I gained deeper understanding of Airflow's execution model, especially how tasks communicate and how the scheduler operates.

3. **ETL Best Practices:** I learned the importance of:
   - Clear separation of extract, transform, and load functions
   - Proper data validation and error handling
   - Efficient data passing between pipeline stages

4. **Monitoring and Observability:** Implementing detailed logging and monitoring was essential for troubleshooting and ensuring pipeline health.

### Conclusion

Completing this assignment provided valuable hands-on experience with Airflow and ETL pipeline development. The challenges encountered, particularly around Windows compatibility, pushed me to explore containerization solutions that are more aligned with real-world production environments.

The final solution is robust, maintainable, and follows industry best practices for data pipeline design. The experience gained from overcoming these challenges will be directly applicable to future data engineering work. 