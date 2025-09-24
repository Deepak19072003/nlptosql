# NLP-to-SQL API

A FastAPI service that converts natural language questions into PostgreSQL SQL queries using Google's Gemini AI model.

## Features

- 🧠 **AI-Powered**: Uses Google Gemini for natural language understanding
- 🛡️ **Secure**: Built-in SQL injection protection and query validation
- 🚀 **Fast**: Optimized for performance with connection pooling
- 🐳 **Containerized**: Ready for Docker deployment
- 📊 **Database**: Supports PostgreSQL with read-only queries

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Google Gemini API key
- PostgreSQL database URL

### Environment Setup

Create a `.env` file:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
```

### Run with Docker

```bash
# Build and start the service
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

The API will be available at `http://localhost:8000`

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/test/llm` | GET | Test Gemini connection |
| `/test/db` | GET | Test database connection |
| `/ask` | POST | Convert natural language to SQL |

### Usage Example

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many products cost more than $100?"}'
```

### Database Schema

The API works with these tables:
- `customers(id, name, email)`
- `products(id, name, price)`
- `orders(id, customer_id, product_id, quantity, order_date)`

### Testing

Import `nlp-to-sql-api.postman_collection.json` into Postman for comprehensive API testing.

### Safety Features

- ✅ Only SELECT queries allowed
- ✅ Query result limit (200 rows max)
- ✅ Statement timeout (5 seconds)
- ✅ Allowed tables whitelist
- ✅ SQL injection protection

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload
```

### Docker Commands

```bash
# Build image
docker build -t nlp-to-sql-api .

# Run container
docker run -p 8000:8000 --env-file .env nlp-to-sql-api

# View logs
docker-compose logs -f
```
