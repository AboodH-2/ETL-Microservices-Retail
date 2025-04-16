# ETL-Microservices-Retail - Documentation

## 1. Project Overview

This project extends the original ETL (Extract, Transform, Load) pipeline using a microservices architecture implemented with Docker containers. The application is composed of multiple interconnected components:

1. **Frontend Web Server**: Provides a user interface to visualize sales data and trigger ETL processes
2. **Backend API Server**: Exposes RESTful endpoints to access data and run ETL operations
3. **PostgreSQL Database**: Stores source data (online sales records)
4. **MySQL Database**: Stores the transformed and aggregated sales data

## 2. Architecture Design

The architecture follows a modern microservices approach with clearly separated concerns:

```
                    +-------------------+
                    |                   |
                    |   Load Balancer   |  (Optional for scaling)
                    |                   |
                    +--------+----------+
                             |
              +-----------------------------+
              |              |              |
   +----------v----+  +------v------+  +---v----------+
   |               |  |             |  |              |
   |   Frontend    |  |  Frontend   |  |  Frontend    |  (Multiple instances possible)
   |   Instance 1  |  |  Instance 2 |  |  Instance N  |
   |               |  |             |  |              |
   +-------+-------+  +------+------+  +------+-------+
           |                 |                |
           +-----------------+-----------------+
                             |
                    +--------v----------+
                    |                   |
                    |   Backend API     |
                    |     Server        |
                    |                   |
                    +--------+----------+
                             |
                +------------+-------------+
                |                          |
      +---------v---------+    +-----------v--------+
      |                   |    |                    |
      |   PostgreSQL DB   |    |     MySQL DB       |
      |   (Source Data)   |    |  (Processed Data)  |
      |                   |    |                    |
      +-------------------+    +--------------------+
```

### Key Design Decisions:

1. **Service Isolation**: Each component runs in its own container with defined responsibilities
2. **Scalability**: Frontend and backend services can be scaled horizontally
3. **Containerization**: Docker ensures consistent environments across development and production
4. **Network Isolation**: Docker networks provide secure communication between services
5. **Persistence**: Docker volumes ensure data persistence across container restarts

## 3. Dockerfiles

### 3.1 Frontend Web Server Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

This Dockerfile:
- Uses Python 3.9 as the base image
- Sets up a working directory inside the container
- Installs required dependencies
- Copies the application code
- Exposes port 5000 for the web interface
- Starts the Flask application

### 3.2 Backend API Server Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "app.py"]
```

This Dockerfile:
- Uses Python 3.9 as the base image
- Sets up a working directory inside the container
- Installs required dependencies including database connectors
- Copies the application code
- Exposes port 5001 for the API
- Starts the Flask API application

## 4. Docker Compose Configurations

### 4.1 Basic Docker Compose (docker-compose.yml)

The basic configuration orchestrates the four main services:

```yaml
version: '3'

services:
  # Frontend Web Server
  frontend:
    build: ./frontend
    ports:
      - "8080:5000"
    depends_on:
      - backend-api
    networks:
      - retail-network
    restart: always

  # Backend API Server
  backend-api:
    build: ./backend
    ports:
      - "5001:5001"
    depends_on:
      - postgres-db
      - mysql-db
    networks:
      - retail-network
    restart: always
    volumes:
      - ./backend:/app

  # PostgreSQL Database
  postgres-db:
    image: postgres:13
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=198277
      - POSTGRES_DB=retail
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./postgres-init:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - retail-network
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 5s
      retries: 5

  # MySQL Database
  mysql-db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=root
      - MYSQL_DATABASE=retail_dw
      - MYSQL_USER=mysql
      - MYSQL_PASSWORD=mysql
    volumes:
      - mysql-data:/var/lib/mysql
      - ./mysql-init:/docker-entrypoint-initdb.d
    ports:
      - "3306:3306"
    networks:
      - retail-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "mysql", "-pmysql"]
      interval: 5s
      retries: 5

networks:
  retail-network:
    driver: bridge

volumes:
  postgres-data:
  mysql-data:
```

Key aspects of this configuration:
- Creates a shared network for inter-service communication
- Maps container ports to host ports
- Sets up environment variables for database configurations
- Creates persistent volumes for database data
- Defines healthchecks to ensure services are properly running

### 4.2 Scaled Docker Compose (docker-compose-scaled.yml)

The scaled configuration adds load balancing and horizontal scaling:

```yaml
version: '3'

services:
  # Load Balancer
  load-balancer:
    image: nginx:latest
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
    depends_on:
      - frontend
      - backend-api
    networks:
      - retail-network
    restart: always

  # Frontend Web Server (scalable)
  frontend:
    build: ./frontend
    expose:
      - "5000"
    depends_on:
      - backend-api
    networks:
      - retail-network
    restart: always
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure

  # Backend API Server (scalable)
  backend-api:
    build: ./backend
    expose:
      - "5001"
    depends_on:
      - postgres-db
      - mysql-db
    networks:
      - retail-network
    restart: always
    volumes:
      - ./backend:/app
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure

  # ... Database configurations remain the same
```

Additional features in the scaled configuration:
- Nginx load balancer to distribute traffic
- Multiple replicas of frontend and backend services
- Rolling update configuration for zero-downtime deployments
- Port exposure only within the Docker network (not directly to host)

## 5. Network Configuration

The project uses a Docker bridge network called `retail-network` that allows the containers to communicate with each other using their service names as hostnames. This provides:

1. **Name resolution**: Services can reference each other by name (e.g., "backend-api" or "mysql-db")
2. **Isolation**: The network is isolated from other container networks
3. **Security**: Only containers on the same network can communicate with each other

## 6. Deployment Instructions

### 6.1 Basic Deployment

To deploy the application with the basic configuration:

1. Clone the repository
2. Navigate to the project directory
3. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

Alternatively, manually execute:
```bash
docker-compose up -d --build
```

### 6.2 Scaled Deployment

To deploy the application with load balancing and multiple service instances:

1. Run the scaled deployment script:
   ```bash
   ./deploy-scaled.sh
   ```

Alternatively, manually execute:
```bash
docker-compose -f docker-compose-scaled.yml up -d --build
```

## 7. Testing and Usage

### 7.1 Basic Usage

After deployment, the application is accessible at:
- Frontend: http://localhost:8080
- Backend API: http://localhost:5001/sales

You can test the ETL pipeline by:
1. Accessing the frontend interface
2. Clicking the "Run ETL Pipeline" button
3. Observing the results on the dashboard after completion

### 7.2 API Endpoints

The backend API provides these endpoints:

- **GET /sales**: Returns the current aggregated sales data
- **POST /run-etl**: Triggers the ETL pipeline execution

Example API usage with curl:
```bash
# Get sales data
curl http://localhost:5001/sales

# Run ETL pipeline
curl -X POST http://localhost:5001/run-etl
```

## 8. Scaling Strategies

### 8.1 Horizontal Scaling

The application supports horizontal scaling through:

1. **Multiple service instances**: The docker-compose-scaled.yml file configures multiple instances of frontend and backend services
2. **Load balancing**: Nginx distributes incoming traffic across these instances
3. **Stateless services**: The frontend and backend are designed to be stateless, allowing for easy scaling

### 8.2 Scaling with Docker Compose

To manually adjust the number of service instances:

```bash
# Scale to 5 backend API instances
docker-compose -f docker-compose-scaled.yml up -d --scale backend-api=5
```

### 8.3 Advanced Scaling with Docker Swarm or Kubernetes

For production environments, consider:

1. **Docker Swarm**: Enables cluster management and native service discovery
   ```bash
   # Initialize swarm
   docker swarm init
   
   # Deploy as a stack
   docker stack deploy -c docker-compose-scaled.yml retail-sales
   ```

2. **Kubernetes**: For more advanced orchestration, the application can be migrated to Kubernetes using:
   ```bash
   # Convert docker-compose to Kubernetes manifests
   kompose convert -f docker-compose-scaled.yml
   
   # Apply the generated manifests
   kubectl apply -f .
   ```

## 9. Monitoring and Logging

The application logs are accessible through Docker's logging system:

```bash
# View logs for all services
docker-compose logs

# Stream logs for a specific service
docker-compose logs -f backend-api
```

For production environments, consider integrating:
1. Prometheus for metrics collection
2. Grafana for visualization
3. ELK Stack (Elasticsearch, Logstash, Kibana) for centralized logging

## 10. Future Improvements

Potential enhancements for the system:

1. **Circuit breaker implementation**: To handle failures gracefully
2. **API authentication**: Secure the API with JWT or OAuth
3. **Container health monitoring**: Advanced health checks and auto-recovery
4. **CI/CD pipeline**: Automated testing and deployment
5. **Message queue**: Implement async processing with RabbitMQ or Kafka for ETL jobs 