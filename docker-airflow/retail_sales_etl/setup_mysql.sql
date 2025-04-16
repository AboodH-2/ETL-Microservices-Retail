-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS retail_dw;

-- Use the database
USE retail_dw;

-- Create table for aggregated sales data
CREATE TABLE IF NOT EXISTS aggregated_sales (
    product_id INT PRIMARY KEY,
    total_quantity INT,
    total_sale_amount DECIMAL(12, 2)
);

-- Optional: Create a user with necessary privileges
CREATE USER IF NOT EXISTS 'mysql'@'localhost' IDENTIFIED BY 'mysql';
GRANT ALL PRIVILEGES ON retail_dw.* TO 'mysql'@'localhost';
FLUSH PRIVILEGES;