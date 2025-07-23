# AI Chatbot with Streamlit & OpenAI

A powerful AI-powered chatbot application built with Streamlit, OpenAI GPT models, and LlamaIndex. The application supports document processing, PostgreSQL database querying, and general chat capabilities with a clean, minimalist interface.

## Features

- **Document Processing**: Upload and query PDF, TXT, and DOCX files
- **Database Integration**: Connect to PostgreSQL databases and query with natural language
- **Intelligent Routing**: Automatically routes queries to documents, database, or general chat
- **Customizable Settings**: Adjustable temperature and model selection
- **Clean UI**: Minimalist Streamlit interface with chat bubbles and organized sidebar
- **Vector Search**: Uses ChromaDB for efficient document similarity search
- **SQL Generation**: Converts natural language to SQL queries
- **Source Citations**: Shows document sources and SQL queries for transparency
- **Docker Integration**: Containerized ChromaDB and PostgreSQL for easy deployment
- **Persistent Storage**: Data survives container restarts

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   PostgreSQL    │    │    ChromaDB     │
│   (Frontend)    │◄──►│   (Structured   │    │   (Vector DB)   │
│   Port: 8501    │    │    Data)        │    │   Port: 8000    │
│                 │    │   Port: 5432    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Docker      │
                    │    Network      │
                    └─────────────────┘
```

## Requirements

- Python 3.8 or higher
- OpenAI API key
- Docker and Docker Compose (recommended)
- PostgreSQL database (optional, for database features)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-chatbot
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Docker Setup (Recommended)

For the complete experience with both PostgreSQL and ChromaDB, use Docker:

1. **Install Docker and Docker Compose** on your system

2. **Start all services with Docker:**
   ```bash
   # Start PostgreSQL, ChromaDB, and pgAdmin
   docker-compose up -d
   
   # Check if containers are running
   docker-compose ps
   ```

3. **Services will be available at:**
   - **PostgreSQL**: `localhost:5432`
   - **ChromaDB**: `localhost:8000`
   - **pgAdmin** (optional): `http://localhost:8181`
     - Email: `admin@chatbot.local`
     - Password: `admin`

4. **Use the Docker environment configuration:**
   ```bash
   # Copy the Docker environment file
   cp .env.docker .env
   
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Stop all services when done:**
   ```bash
   docker-compose down
   ```

The Docker setup includes:
- **PostgreSQL 15** database with sample data
- **ChromaDB** vector database for document storage
- Pre-configured users and permissions
- Optional **pgAdmin** for database management
- Sample tables (customers, orders, products, order_items)
- Useful views for testing queries
- Persistent data volumes

### Individual Service Management

You can also start services individually:

```bash
# Start only PostgreSQL
docker-compose up -d postgres

# Start only ChromaDB
docker-compose up -d chromadb

# Start only pgAdmin
docker-compose up -d pgadmin
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=your_database
POSTGRES_USERNAME=your_username
POSTGRES_PASSWORD=your_password

# Optional - Application Settings
MAX_FILE_SIZE_MB=10
MAX_DOCUMENTS=100
```

### Default Settings

The application comes with sensible defaults:
- **Temperature**: 0.7
- **Model**: gpt-3.5-turbo
- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Max Conversation History**: 20 messages

## Usage

1. **Start the Docker services (recommended):**
   ```bash
   docker-compose up -d
   ```

2. **Start the application:**
   ```bash
   streamlit run app.py
   ```

3. **Access the application:**
   Open your browser and navigate to `http://localhost:8501`

### Verifying Installation

You can test your installation with the included test scripts:

```bash
# Test all imports and connections
python test_imports.py

# Test imports in Streamlit context
streamlit run test_streamlit_imports.py --server.port 8502
```

### Document Processing

1. **Upload Documents:**
   - Use the file uploader in the sidebar
   - Supported formats: PDF, TXT, DOCX
   - Maximum size: 10MB per file
   - Files are automatically processed and indexed

2. **Query Documents:**
   - Ask questions about uploaded documents
   - Example: "What is the main topic of the document?"
   - Sources are automatically cited in responses

### Database Querying

1. **Connect to Database:**
   - Fill in connection details in the sidebar
   - Test connection before connecting
   - Browse available tables and schemas

2. **Query with Natural Language:**
   - Ask questions about your data
   - Example: "Show me all customers from last month"
   - SQL queries are generated and displayed
   - Results are shown in table format

### General Chat

- Ask general questions when no documents or database are connected
- Powered by OpenAI GPT models
- Adjustable temperature and model selection

## 🔍 Sample Database Queries

<details>
<summary>Click to expand sample queries for testing</summary>

Once you have the Docker PostgreSQL database running, you can test these natural language queries:

### Database Schema
The Docker setup creates these tables with sample data:
- **customers** - Customer information (10 sample customers)
- **products** - Product catalog (10 sample products) 
- **orders** - Order records (10 sample orders)
- **order_items** - Individual items in each order
- **order_summary** (view) - Combined order and customer information
- **product_sales** (view) - Product sales statistics

### Basic Queries
**Customer Information:**
- "How many customers do we have?"
- "Show me all customers from the USA"
- "What is John Doe's email address?"
- "List all customers in New York"

**Product Information:**
- "How many products are in stock?"
- "Show me all products in the Electronics category"
- "What is the most expensive product?"
- "List all products under $50"

**Order Information:**
- "How many orders were placed this month?"
- "Show me all completed orders"
- "What is the total value of all orders?"
- "Which customer has the most orders?"

### Advanced Queries
**Sales Analysis:**
- "What are the top 5 best-selling products?"
- "Show me total revenue by product category"
- "Which products have never been ordered?"
- "What is the average order value?"

**Customer Analysis:**
- "Who are our top 3 customers by total spending?"
- "Show me customers who haven't ordered recently"
- "What is the average customer lifetime value?"

**Inventory & Trends:**
- "Which products are running low on stock?"
- "Show me monthly sales trends"
- "What categories generate the most revenue?"

</details>

## 📁 Project Structure

```
ai_chatbot/
├── app.py                 # Main Streamlit application
├── docker-compose.yml     # Docker configuration for all services
├── config/
│   └── settings.py        # Configuration settings
├── src/
│   ├── document_handler.py    # Document processing logic
│   ├── database_handler.py    # Database connectivity
│   ├── chat_engine.py         # Chat logic and routing
│   └── utils.py              # Utility functions
├── docker/
│   └── init-db/
│       └── 01-init-sample-data.sql  # Sample database setup
├── uploads/               # Temporary file storage
├── data/                 # ChromaDB storage (when running locally)
├── test_imports.py       # Test script for import verification
├── test_streamlit_imports.py  # Streamlit test for imports
├── .env                  # Environment variables
├── .env.example          # Example environment file
├── .env.docker           # Docker environment template
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## 🔧 Technical Details

### LlamaIndex Integration

The application uses LlamaIndex for:
- **Document Processing**: VectorStoreIndex for semantic search
- **Database Queries**: SQLDatabase for natural language to SQL conversion
- **Embeddings**: OpenAI text-embedding-ada-002
- **Vector Storage**: ChromaDB for persistent storage (Docker or local)

### ChromaDB Integration

- **Docker Deployment**: ChromaDB runs in a separate container at `localhost:8000`
- **HTTP Client**: Application connects via ChromaDB HTTP API
- **Persistent Storage**: Vector data survives container restarts
- **Collection Management**: Documents are stored in the "documents" collection
- **Health Monitoring**: Container health checks ensure service availability

### Security Features

- Environment variable storage for API keys
- Input validation and sanitization
- SQL injection protection (SELECT queries only)
- File type and size validation
- Secure file upload handling

### Performance Optimizations

- Persistent vector storage with ChromaDB
- Conversation history management (20 message limit)
- Efficient document chunking (1000 chars with 200 overlap)
- Connection pooling for database operations

## Example Use Cases

### Document Analysis
```
User: "What are the key findings in the research paper?"
Assistant: Based on the uploaded document, the key findings include... [with source citations]
```

### Database Queries
```
User: "How many orders were placed last month?"
Assistant: I found 1,247 orders placed last month. Here's the breakdown... [with SQL query shown]

User: "Show me the top 5 customers by total order value"
Assistant: Here are the top 5 customers by total order value... [with data table]

User: "What products are in the Electronics category?"
Assistant: I found 5 products in the Electronics category... [with results table]
```

### General Questions
```
User: "Explain machine learning in simple terms"
Assistant: Machine learning is a type of artificial intelligence that...
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error:**
   - Ensure your API key is correctly set in the `.env` file
   - Check that the API key has sufficient credits

2. **Database Connection Failed:**
   - Verify database credentials
   - Ensure PostgreSQL server is running (or Docker container is up)
   - Check network connectivity
   - For Docker: Run `docker-compose ps` to check container status
   - For Docker: Run `docker-compose logs postgres` to check PostgreSQL logs

3. **ChromaDB Connection Failed:**
   - Ensure ChromaDB Docker container is running: `docker-compose up -d chromadb`
   - Check ChromaDB status: `docker-compose logs chromadb`
   - Verify ChromaDB is accessible: `curl http://localhost:8000`
   - For connection issues, restart the container: `docker-compose restart chromadb`

4. **Document Processing Errors:**
   - Verify file format is supported (PDF, TXT, DOCX)
   - Check file size (max 10MB)
   - Ensure file is not corrupted
   - Check ChromaDB connection (documents are stored in vector database)

5. **Import Errors:**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+)
   - Activate virtual environment
   - For LlamaIndex issues, try: `pip install --upgrade llama-index-core llama-index-llms-openai llama-index-embeddings-openai llama-index-vector-stores-chroma`
   - Run the test script: `python test_imports.py`

### Performance Issues

1. **Slow Document Processing:**
   - Large files take longer to process
   - Consider breaking large documents into smaller files
   - Check system resources

2. **Slow Database Queries:**
   - Optimize database indexes
   - Consider query complexity
   - Check database connection

## Updates and Maintenance

### Updating Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Clearing Vector Database

**For Docker ChromaDB:**
```bash
# Stop and remove ChromaDB container and its data
docker-compose down chromadb
docker volume rm ai-chatbot_chroma_data
docker-compose up -d chromadb
```

**For local ChromaDB:**
Delete the `data/` directory to reset the vector database:
```bash
rm -rf data/
```

### Docker Management

```bash
# View all container logs
docker-compose logs

# View specific service logs
docker-compose logs chromadb
docker-compose logs postgres

# Restart a specific service
docker-compose restart chromadb

# Update container images
docker-compose pull
docker-compose up -d

# Clean up Docker resources
docker system prune
```

### Monitoring Usage
Check the Streamlit logs for application performance and errors.

## Development

## Development

<details>
<summary>Click to expand implementation details</summary>

### ✅ Implementation Summary

The complete AI Chatbot application has been successfully implemented with all requested features:

#### Core Requirements Met:
1. **Streamlit UI** - Clean, minimalist interface with sidebar controls
2. **Document Upload** - PDF, TXT, DOCX support with drag-and-drop
3. **PostgreSQL Integration** - Full database connectivity and querying
4. **Temperature Control** - Adjustable via sidebar slider (0.0-2.0)
5. **File Management** - Upload, view, and delete documents
6. **LlamaIndex Framework** - Complete integration for documents and SQL

#### Advanced Features:
- **Intelligent Query Routing** - Auto-detects document vs database vs general queries
- **Vector Search** - ChromaDB for persistent document embeddings
- **Natural Language to SQL** - Converts questions to SQL queries
- **Source Citations** - Shows document sources and SQL queries
- **Session Management** - Conversation history with 20-message limit
- **Error Handling** - Comprehensive validation and error messages
- **Security** - Input sanitization, SQL injection protection

#### UI Components:
- **Sidebar Sections:**
  - File upload with progress indicators
  - Database connection form with test capability
  - Table browser with schema information
  - Model and temperature controls
  - Uploaded files management
- **Main Chat Interface:**
  - Message bubbles with role-based styling
  - Source citations for responses
  - SQL query display for database responses
  - Conversation history management

#### Technical Architecture:
- **Document Processing:** LlamaIndex + ChromaDB for vector storage
- **Database Integration:** SQLAlchemy + PostgreSQL with natural language processing
- **Chat Management:** Intelligent routing between document, database, and general queries
- **State Management:** Streamlit session state for persistent user data
- **Docker Integration:** Containerized PostgreSQL and ChromaDB services

</details>

### Adding New Document Types

1. Update `SUPPORTED_FILE_TYPES` in `config/settings.py`
2. Add extraction logic in `document_handler.py`
3. Test with sample files

### Extending Database Support

1. Add new database engine in `database_handler.py`
2. Update connection string validation
3. Test with target database

### Customizing UI

1. Modify CSS in `app.py`
2. Update Streamlit components
3. Test responsive design

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing issues in the repository
3. Create a new issue with detailed information

## Future Enhancements

- [ ] Support for additional file formats (XLSX, CSV, etc.)
- [ ] Multi-database support (MySQL, SQLite, etc.)
- [ ] Advanced document analytics
- [ ] User authentication and session management
- [ ] API endpoint for programmatic access
- [ ] Enhanced error handling and logging
- [ ] Performance monitoring and analytics
- [ ] Custom embedding models
- [ ] Conversation memory across sessions
- [ ] ChromaDB clustering for scalability
- [ ] Multi-tenant document isolation
- [ ] Advanced vector search filtering
- [ ] Real-time document synchronization
- [ ] Integration with cloud storage (S3, Google Drive)

## Quick Troubleshooting Commands

```bash
# Check all services status
docker-compose ps

# Test imports
python test_imports.py

# Test ChromaDB connection
curl http://localhost:8000

# Test PostgreSQL connection
docker exec ai-chatbot-postgres psql -U chatbot_user -d ai_chatbot -c "SELECT version();"

# View application logs
streamlit run app.py --logger.level debug

# Reset everything
docker-compose down
docker volume prune
docker-compose up -d
```