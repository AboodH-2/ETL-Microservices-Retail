-- Create the online_sales table
CREATE TABLE IF NOT EXISTS online_sales (
    sale_id SERIAL PRIMARY KEY,
    product_id INT,
    quantity INT,
    sale_amount DECIMAL(10, 2),
    sale_date DATE
);

-- Insert sample data
INSERT INTO online_sales (product_id, quantity, sale_amount, sale_date) VALUES
(101, 2, 40.00, '2024-03-01'),
(102, 1, 20.00, '2024-03-01'),
(103, 3, 60.00, '2024-03-02'),
(101, 1, 20.00, '2024-03-02'),
(104, 2, 35.00, '2024-03-03'),
(102, 3, 60.00, '2024-03-03'),
(103, 1, 20.00, '2024-03-04'),
(104, 2, 35.00, '2024-03-04'),
(101, 4, 80.00, '2024-03-05'),
(105, 1, 25.00, '2024-03-05'); 