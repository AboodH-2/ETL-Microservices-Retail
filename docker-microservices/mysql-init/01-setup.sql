-- Use the database
USE retail_dw;

-- Create table for aggregated sales data
CREATE TABLE IF NOT EXISTS aggregated_sales (
    product_id INT PRIMARY KEY,
    total_quantity INT,
    total_sale_amount DECIMAL(12, 2)
); 