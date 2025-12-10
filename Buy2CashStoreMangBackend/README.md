# BuyCash Store Management - AI-Powered Store Analytics & Search System

A comprehensive store management system with AI-powered search, dynamic MongoDB queries, Redis session tracking, and advanced business analytics for grocery stores.

## Features

### Core Store Management
- **Store Analytics**: Comprehensive performance metrics, revenue tracking, and business insights
- **Product Analytics**: Top-selling products, unsold inventory, and category performance analysis
- **Customer Behavior**: Popular search queries with contextual categories (dishbased)
- **Session Management**: Redis-powered search session tracking with 24-hour expiry

### AI-Powered Search & Recommendations
- **Natural Language Search**: Convert user queries like "list categories" into MongoDB filters
- **Dynamic Query Processing**: AI generates MongoDB queries from natural language
- **GPT-4o Mini Integration**: Cost-efficient AI responses with external prompt management
- **Product Substitutions**: AI-powered alternatives when products are out of stock
- **Discount Recommendations**: Machine learning insights for pricing strategies

### Advanced Features
- **Redis Session Tracking**: Unique session IDs with comprehensive metadata storage
- **MongoDB Query Generation**: Dynamic database queries from user messages
- **Category Discovery**: Intelligent category finding through product relationships
- **Performance Benchmarking**: Store performance analysis and recommendations

### Tech Stack

### Backend
- **FastAPI**: Modern async Python web framework
- **MongoDB**: NoSQL database with complex aggregation pipelines
- **Redis**: Session storage and caching
- **OpenAI GPT-4o Mini**: Cost-efficient AI responses
- **Supabase**: Analytics data storage
- **Pydantic v2**: Data validation and serialization

### Core Libraries
- **httpx**: Async HTTP client for testing
- **pytest-asyncio**: Async testing framework
- **pymongo**: MongoDB driver
- **python-dotenv**: Environment configuration

## Prerequisites

- Python 3.8+
- MongoDB database
- Redis server
- OpenAI API key (for GPT-4o Mini)
- Supabase account (for analytics)

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd BuyCash-Store-Management
```

### 2. Backend Setup

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Set up Environment Variables
Create a `config.env` file in the root directory:
```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net
MONGODB_DB=buy2cash

# Supabase Configuration  
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# OpenAI Configuration (GPT-4o mini)
OPENAI_API_KEY=your-openai-api-key-here

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

#### Run the Backend
```bash
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

## Docker Deployment

### Prerequisites for Docker
- Docker installed on your system
- Docker Desktop running (for Windows/Mac)

### Using Docker (Recommended for Production)

#### 1. Pull and Run (if image is available on registry)
```bash
# Pull the Docker image from registry
docker pull buycash-store-management

# Run the container with environment file
docker run -p 8000:8000 --env-file config.env buycash-store-management
```

#### 2. Build and Run Locally
```bash
# Build the Docker image
docker build -t buycash-store-management .

# Run the container
docker run -p 8000:8000 --env-file config.env buycash-store-management
```

#### 3. Run in Background (Detached Mode)
```bash
# Run container in background
docker run -d -p 8000:8000 --env-file config.env --name buycash-api buycash-store-management

# View logs
docker logs buycash-api

# Stop the container
docker stop buycash-api
```

### Access the Application
Once the Docker container is running:
- **API Base URL**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Docker Best Practices
- The application runs on port 8000 inside the container
- Environment variables are loaded from `config.env` at runtime
- Container includes all dependencies and is ready for production deployment
- Use `-d` flag for background execution in production environments

## API Endpoints

### Store Management
- `GET /health` - Health check with system status
- `GET /api/stores` - Get all approved and active stores

### Analytics Endpoints
- `GET /api/analytics/top-selling-products/{store_id}` - Top selling products with categories and units
- `GET /api/analytics/popular-searches/{store_id}` - Popular customer searches (sno, contextual_category, search_query)
- `GET /api/analytics/top-selling-categories/{store_id}` - Top selling categories with subcategories
- `GET /api/analytics/unsold-products/{store_id}` - Unsold/stagnant products needing attention
- `GET /api/analytics/store-performance/{store_id}` - Store performance and payout metrics

### Chat
- `POST /query` - **NLP-powered search** - converts natural language to MongoDB queries, generates AI responses
- `GET /api/sessions` - List all query sessions stored in Redis (with optional store filtering)
- `GET /api/sessions/{session_id}` - Get specific query session details by ID

### AI Features
- `GET /stores/{store_id}/products/{product_id}/substitutions` - AI-powered product alternatives
- `GET /stores/{store_id}/recommendations/discounts` - AI-generated discount recommendations

## Usage Guide

### Chat

The core innovation of BuyCash is the intelligent search system:

1. **Natural Language Input**: Users can ask questions like:
   - "list the categories"
   - "products under 100 rupees"
   - "show me out of stock items"

2. **AI Processing**: The system:
   - Converts natural language to MongoDB filters using GPT-4o Mini
   - Executes dynamic database queries
   - Generates natural language responses
   - Saves complete sessions in Redis

### Store Analytics Dashboard

- **Performance Metrics**: Revenue, completion rates, order statistics
- **Product Insights**: Best sellers, slow movers, inventory analysis
- **Customer Behavior**: Search patterns and popular queries
- **AI Recommendations**: Discount strategies and product substitutions

## Configuration

### Redis Session Configuration
- **Key Pattern**: `nlp_session:{session_id}`
- **Expiry**: 24 hours
- **Data**: Complete query metadata with store context

### MongoDB Integration
- **Dynamic Queries**: AI-generated filters based on user input
- **Complex Aggregations**: Category discovery through product relationships
- **Performance Optimized**: Efficient querying with proper indexing

## Project Structure

```
BuyCash-Store-Management/
├── main.py                     # FastAPI application entry point
├── config.env                  # Environment configuration
├── requirements.txt            # Python dependencies
├── app/
│   ├── __init__.py
│   ├── models.py              # Pydantic models
│   ├── database.py            # MongoDB and Redis connections
│   ├── core.py                # Business logic and utilities
│   ├── ai_prompts.py          # External AI prompt management
│   ├── ai_service.py          # GPT-4o Mini integration
│   ├── services.py            # Business services
│   └── api.py                 # FastAPI routes
└── README.md
```

## Key Innovations

### 1. Dynamic Query Generation
- **Problem Solved**: Traditional search requires predefined filters
- **Our Solution**: AI converts "show cheap products" → `{"offerPrice": {"$lt": 100}}`

### 2. Category Intelligence
- **Problem Solved**: Categories lack seller IDs in MongoDB
- **Our Solution**: Find categories through product relationships

### 3. Session Persistence
- **Problem Solved**: No tracking of user interactions
- **Our Solution**: Redis-based session management with rich metadata

### 4. Cost-Efficient AI
- **Problem Solved**: Expensive AI operations
- **Our Solution**: GPT-4o Mini with optimized prompts and caching

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- API Documentation: `http://localhost:8000/docs` (when running)
- Create an issue in the repository
- Check the comprehensive test suite for usage examples



