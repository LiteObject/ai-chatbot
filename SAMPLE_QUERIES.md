# Sample Database Queries for Testing

This document contains sample natural language queries you can test with the AI Chatbot once you have the Docker PostgreSQL database running.

## 📊 Sample Database Schema

The Docker setup creates the following tables with sample data:

### Tables:
- **customers** - Customer information (10 sample customers)
- **products** - Product catalog (10 sample products)
- **orders** - Order records (10 sample orders)
- **order_items** - Individual items in each order

### Views:
- **order_summary** - Combined order and customer information
- **product_sales** - Product sales statistics

## 🔍 Sample Natural Language Queries

### Basic Queries

#### Customer Information
- "How many customers do we have?"
- "Show me all customers from the USA"
- "What is John Doe's email address?"
- "List all customers in New York"

#### Product Information
- "How many products are in stock?"
- "Show me all products in the Electronics category"
- "What is the most expensive product?"
- "List all products under $50"

#### Order Information
- "How many orders were placed this month?"
- "Show me all completed orders"
- "What is the total value of all orders?"
- "Which customer has the most orders?"

### Intermediate Queries

#### Sales Analysis
- "What are the top 5 best-selling products?"
- "Show me total revenue by product category"
- "Which products have never been ordered?"
- "What is the average order value?"

#### Customer Analysis
- "Who are our top 3 customers by total spending?"
- "Show me customers who haven't placed any orders"
- "What is the average number of items per order?"
- "Which cities have the most customers?"

#### Inventory and Business Intelligence
- "Which products are running low on stock?"
- "Show me orders with status 'pending'"
- "What is the total revenue for completed orders?"
- "How many different products have been sold?"

### Advanced Queries

#### Time-based Analysis
- "Show me orders placed in January 2024"
- "What products were ordered most recently?"
- "Which month had the highest sales?"

#### Complex Relationships
- "Show me customer details for orders over $1000"
- "List products that appear in multiple orders"
- "Which customers bought Electronics products?"
- "Show me the order details for customer John Doe"

#### Aggregation and Statistics
- "What is the total quantity of each product sold?"
- "Show me revenue breakdown by customer"
- "What is the average price per category?"
- "How many orders contain more than 2 items?"

## 🎯 Query Testing Tips

1. **Start Simple**: Begin with basic queries to test the connection
2. **Be Specific**: Use exact table/column names when needed
3. **Natural Language**: The AI understands conversational queries
4. **Follow Up**: Ask follow-up questions to drill down into data
5. **Check Results**: Verify SQL queries and results make sense

## 📋 Expected Results Examples

### "How many customers do we have?"
- **Expected SQL**: `SELECT COUNT(*) FROM customers`
- **Expected Result**: 10 customers

### "Show me all products in the Electronics category"
- **Expected SQL**: `SELECT * FROM products WHERE category = 'Electronics'`
- **Expected Result**: 5 products (Laptop Pro, Wireless Mouse, Smartphone, Tablet, Headphones)

### "What are the top 3 customers by total spending?"
- **Expected SQL**: Complex JOIN with aggregation
- **Expected Result**: Customer names with their total order amounts

## 🔧 Troubleshooting Queries

If queries don't work as expected:

1. **Check Connection**: Ensure database is running (`docker-compose ps`)
2. **Verify Tables**: Ask "What tables are available?" first
3. **Simple Test**: Try "SELECT 1" to test basic connectivity
4. **Table Structure**: Ask "Describe the customers table"

## 🚀 Getting Started

1. Start the database:
   ```bash
   python docker_db_manager.py
   # Or directly: docker-compose up -d
   ```

2. Configure your `.env` file with the Docker database settings

3. Launch the AI Chatbot:
   ```bash
   streamlit run app.py
   ```

4. Connect to the database in the sidebar using:
   - Host: localhost
   - Port: 5432
   - Database: ai_chatbot
   - Username: chatbot_user
   - Password: chatbot_password

5. Start asking questions from the samples above!
