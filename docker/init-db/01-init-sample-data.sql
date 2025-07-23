-- Sample database initialization script for AI Chatbot
-- This script creates sample tables and data for testing

-- Create a sample customers table
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    city VARCHAR(50),
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a sample orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date DATE DEFAULT CURRENT_DATE,
    total_amount DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a sample products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    category VARCHAR(50),
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a sample order_items table
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2),
    total_price DECIMAL(10,2)
);

-- Insert sample data into customers
INSERT INTO customers (name, email, phone, city, country) VALUES
    ('John Doe', 'john.doe@email.com', '+1-555-0101', 'New York', 'USA'),
    ('Jane Smith', 'jane.smith@email.com', '+1-555-0102', 'Los Angeles', 'USA'),
    ('Bob Johnson', 'bob.johnson@email.com', '+1-555-0103', 'Chicago', 'USA'),
    ('Alice Brown', 'alice.brown@email.com', '+1-555-0104', 'Houston', 'USA'),
    ('Charlie Wilson', 'charlie.wilson@email.com', '+1-555-0105', 'Phoenix', 'USA'),
    ('Diana Davis', 'diana.davis@email.com', '+1-555-0106', 'Philadelphia', 'USA'),
    ('Frank Miller', 'frank.miller@email.com', '+1-555-0107', 'San Antonio', 'USA'),
    ('Grace Lee', 'grace.lee@email.com', '+1-555-0108', 'San Diego', 'USA'),
    ('Henry Clark', 'henry.clark@email.com', '+1-555-0109', 'Dallas', 'USA'),
    ('Ivy Rodriguez', 'ivy.rodriguez@email.com', '+1-555-0110', 'San Jose', 'USA')
ON CONFLICT (email) DO NOTHING;

-- Insert sample data into products
INSERT INTO products (name, description, price, category, stock_quantity) VALUES
    ('Laptop Pro', 'High-performance laptop for professionals', 1299.99, 'Electronics', 50),
    ('Wireless Mouse', 'Ergonomic wireless mouse with long battery life', 29.99, 'Electronics', 200),
    ('Office Chair', 'Comfortable ergonomic office chair', 199.99, 'Furniture', 25),
    ('Desk Lamp', 'LED desk lamp with adjustable brightness', 49.99, 'Furniture', 75),
    ('Coffee Mug', 'Ceramic coffee mug with company logo', 12.99, 'Office Supplies', 100),
    ('Notebook Set', 'Set of 3 professional notebooks', 24.99, 'Office Supplies', 150),
    ('Smartphone', 'Latest smartphone with advanced features', 899.99, 'Electronics', 30),
    ('Tablet', '10-inch tablet for work and entertainment', 399.99, 'Electronics', 40),
    ('Headphones', 'Noise-canceling wireless headphones', 179.99, 'Electronics', 60),
    ('Standing Desk', 'Adjustable height standing desk', 599.99, 'Furniture', 15);

-- Insert sample data into orders
INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES
    (1, '2024-01-15', 1329.98, 'completed'),
    (2, '2024-01-16', 199.99, 'completed'),
    (3, '2024-01-17', 49.99, 'completed'),
    (4, '2024-01-18', 1099.98, 'shipped'),
    (5, '2024-01-19', 24.99, 'completed'),
    (6, '2024-01-20', 629.98, 'processing'),
    (7, '2024-01-21', 179.99, 'completed'),
    (8, '2024-01-22', 399.99, 'shipped'),
    (9, '2024-01-23', 42.98, 'completed'),
    (10, '2024-01-24', 1299.99, 'pending');

-- Insert sample data into order_items
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
    (1, 1, 1, 1299.99, 1299.99),
    (1, 2, 1, 29.99, 29.99),
    (2, 3, 1, 199.99, 199.99),
    (3, 4, 1, 49.99, 49.99),
    (4, 7, 1, 899.99, 899.99),
    (4, 3, 1, 199.99, 199.99),
    (5, 6, 1, 24.99, 24.99),
    (6, 10, 1, 599.99, 599.99),
    (6, 2, 1, 29.99, 29.99),
    (7, 9, 1, 179.99, 179.99),
    (8, 8, 1, 399.99, 399.99),
    (9, 5, 2, 12.99, 25.98),
    (9, 6, 1, 24.99, 24.99),
    (10, 1, 1, 1299.99, 1299.99);

-- Create some indexes for better performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

-- Create a view for order summaries
CREATE OR REPLACE VIEW order_summary AS
SELECT 
    o.id as order_id,
    c.name as customer_name,
    c.email as customer_email,
    o.order_date,
    o.total_amount,
    o.status,
    COUNT(oi.id) as item_count
FROM orders o
JOIN customers c ON o.customer_id = c.id
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id, c.name, c.email, o.order_date, o.total_amount, o.status
ORDER BY o.order_date DESC;

-- Create a view for product sales
CREATE OR REPLACE VIEW product_sales AS
SELECT 
    p.id as product_id,
    p.name as product_name,
    p.category,
    p.price,
    COALESCE(SUM(oi.quantity), 0) as total_sold,
    COALESCE(SUM(oi.total_price), 0) as total_revenue
FROM products p
LEFT JOIN order_items oi ON p.id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.id
WHERE o.status IN ('completed', 'shipped') OR o.status IS NULL
GROUP BY p.id, p.name, p.category, p.price
ORDER BY total_revenue DESC;

-- Grant permissions (if needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO chatbot_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO chatbot_user;

-- Print completion message
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully!';
    RAISE NOTICE 'Sample data has been inserted into customers, products, orders, and order_items tables.';
    RAISE NOTICE 'Created views: order_summary, product_sales';
    RAISE NOTICE 'You can now test the AI Chatbot with sample database queries.';
END $$;
