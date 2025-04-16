#!/bin/bash

echo "==============================================="
echo "   ETL-Microservices-Retail Deployment"
echo "          (Scaled with Load Balancer)"
echo "==============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "[1/5] Building and starting all services with load balancer..."
docker-compose -f docker-compose-scaled.yml up -d --build

# Wait for services to be fully up
echo "[2/5] Waiting for services to start..."
sleep 15

# Check if PostgreSQL is up
echo "[3/5] Checking PostgreSQL connection..."
docker-compose -f docker-compose-scaled.yml exec postgres-db pg_isready -U postgres
if [ $? -ne 0 ]; then
    echo "Warning: PostgreSQL might not be fully initialized yet."
fi

# Check if MySQL is up
echo "[4/5] Checking MySQL connection..."
docker-compose -f docker-compose-scaled.yml exec mysql-db mysqladmin ping -h localhost -u mysql -pmysql
if [ $? -ne 0 ]; then
    echo "Warning: MySQL might not be fully initialized yet."
fi

# Display service status
echo "[5/5] Checking service status..."
docker-compose -f docker-compose-scaled.yml ps

echo "==============================================="
echo "   Scaled Deployment Complete!"
echo "==============================================="
echo "Load Balancer: http://localhost"
echo "Direct Frontend: http://localhost:5000 (through load balancer)"
echo "Direct Backend API: http://localhost/api/sales (through load balancer)"
echo ""
echo "To stop the services:"
echo "  docker-compose -f docker-compose-scaled.yml down"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose-scaled.yml logs -f"
echo "===============================================" 