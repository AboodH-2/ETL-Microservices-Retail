# ETL-Microservices-Retail Architecture

This project extends the original ETL pipeline into a full microservices architecture using Docker containers. The application consists of:

1. **Frontend Web Server**: A Flask-based web interface to visualize ETL results and trigger pipeline runs
2. **Backend API Server**: A REST API that exposes ETL functionality and data access
3. **PostgreSQL Database**: Stores the source data (online sales)
4. **MySQL Database**: Stores the transformed and aggregated sales data

## Architecture Diagram

```
+----------------+        +----------------+        +----------------+
|                |        |                |        |                |
|   Frontend     |------->|   Backend API  |------->|   PostgreSQL   |
|  Web Server    |        |     Server     |        |   Database     |
|   (Flask)      |<-------|   (Flask API)  |<-------|                |
|                |        |                |        +----------------+
+----------------+        +----------------+
                                 |
                                 |
                                 v
                          +----------------+
                          |                |
                          |     MySQL      |
                          |   Database     |
                          |                |
                          +----------------+
```

## How to Deploy and Run

### 1. Prerequisites

- Docker and Docker Compose installed on your system

### 2. Deployment Steps

1. Clone this repository:
   ```
   git clone <repository-url>
   cd docker-microservices
   ```

2. Build and start all services using Docker Compose:
   ```
   docker-compose up -d
   ```

3. Access the frontend application:
   - Open your web browser and navigate to: `http://localhost:8080`

4. Directly access the backend API:
   - To get sales data: `http://localhost:5001/sales`
   - To run the ETL pipeline: Send a POST request to `http://localhost:5001/run-etl`

### 3. Testing the Application

1. View the current sales data on the frontend dashboard
2. Click the "Run ETL Pipeline" button to execute the ETL process
3. After the ETL completes, refresh the dashboard to see the updated data

### 4. Components

#### Frontend Web Server
- Port: 8080 (mapped to container port 5000)
- Technology: Flask
- Functions: Visualizes sales data and provides interface to trigger ETL pipeline

#### Backend API Server
- Port: 5001
- Technology: Flask API
- Endpoints:
  - GET /sales - Retrieves aggregated sales data
  - POST /run-etl - Triggers the ETL pipeline

#### PostgreSQL Database
- Port: 5432
- Tables: online_sales

#### MySQL Database
- Port: 3306
- Tables: aggregated_sales

## Scaling and Load Balancing (Optional)

For production environments, you can scale the services horizontally:

### Using Docker Compose Scale Command

```bash
docker-compose up -d --scale backend-api=3
```

This will start 3 instances of the backend API server.

### Using an External Load Balancer

For a more robust solution, you can add a service like Nginx or Traefik as a load balancer:

```yaml
# Sample addition to docker-compose.yml for adding Nginx as a load balancer
load-balancer:
  image: nginx:latest
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  ports:
    - "80:80"
  depends_on:
    - frontend
    - backend-api
  networks:
    - retail-network
```

## Shutting Down

To stop all services:

```bash
docker-compose down
```

To stop and remove all containers, networks, and volumes:

```bash
docker-compose down -v
``` 