# ETL-Microservices-Retail

This repository contains a comprehensive implementation of a retail sales data processing system, developed in two main parts:

## Project Overview

1. **Part 1: ETL Pipeline with Apache Airflow** (in `docker-airflow/`)
   - Extract, Transform, and Load (ETL) pipeline for retail sales data
   - Orchestrated with Apache Airflow
   - Scheduled data processing workflows

2. **Part 2: Microservices Architecture** (in `docker-microservices/`)
   - Extension of the ETL pipeline into a microservices architecture
   - Frontend web application for visualization and user interaction
   - Backend API for data access and ETL trigger
   - Complete containerization with Docker

## Repository Structure

```
ETL-Microservices-Retail/
├── docker-airflow/
│   ├── dags/                  # Airflow DAG definitions
│   ├── logs/                  # Airflow logs
│   ├── plugins/               # Airflow plugins
│   ├── retail_sales_etl/      # ETL core code
│   └── docker-compose.yml     # Docker configuration for Airflow
│
└── docker-microservices/
    ├── frontend/              # Web frontend (Flask)
    │   ├── templates/         # HTML templates
    │   └── Dockerfile
    ├── backend/               # API backend (Flask)
    │   └── Dockerfile
    ├── postgres-init/         # PostgreSQL initialization scripts
    ├── mysql-init/            # MySQL initialization scripts
    ├── docker-compose.yml     # Basic Docker configuration
    └── docker-compose-scaled.yml  # Configuration with scaling and load balancing
```

## Part 1: ETL Pipeline with Apache Airflow

The ETL pipeline processes retail sales data from two sources:
- Online sales data from PostgreSQL database
- In-store sales data from CSV files

The data is cleaned, transformed, and aggregated before being loaded into a MySQL data warehouse.

### Key Features

- Scheduled data processing with Apache Airflow
- Modular ETL functions for easy maintenance
- Data aggregation by product_id
- Error handling and logging

### Running the ETL Pipeline

```bash
# Navigate to the docker-airflow directory
cd docker-airflow

# Start the Airflow containers
docker-compose up -d

# Access Airflow UI at http://localhost:8080
# Username: airflow
# Password: airflow
```

## Part 2: Microservices Architecture

The microservices architecture extends the ETL pipeline into a complete application with:

- Frontend web interface for data visualization and ETL trigger
- Backend API for data access and process control
- Database services (PostgreSQL and MySQL)
- Optional load balancing for horizontal scaling

### Key Features

- Complete isolation of components
- REST API for data access
- Web dashboard for visualization
- Horizontally scalable architecture
- Docker containerization

### Running the Microservices Application

```bash
# Navigate to the docker-microservices directory
cd docker-microservices

# Start the basic configuration
docker-compose up -d

# Or start the scaled configuration with load balancing
docker-compose -f docker-compose-scaled.yml up -d

# Access the frontend at http://localhost:8081
# Access the API directly at http://localhost:5001/sales
```

## Technologies Used

- **Python** - Core programming language
- **Apache Airflow** - Workflow orchestration
- **Flask** - Web application framework
- **PostgreSQL** - Source database
- **MySQL** - Data warehouse
- **Docker & Docker Compose** - Containerization
- **Nginx** - Load balancing (in scaled deployment)

## Notes

- The two parts of the project (Airflow ETL and Microservices) cannot run simultaneously on the same machine due to port conflicts.
- This project demonstrates the evolution from a basic ETL workflow to a complete microservices architecture.

## License

[MIT License](LICENSE) 