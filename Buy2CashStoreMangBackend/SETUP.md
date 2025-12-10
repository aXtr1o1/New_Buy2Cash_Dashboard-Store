# Buy2Cash MongoDB Setup Guide

This guide will help you set up the Buy2Cash application with MongoDB instead of SQLite.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- MongoDB instance (local or cloud)

## Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the root directory with:
   ```
   MONGODB_URL=mongodb://localhost:27017
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Update MongoDB connection:**
   - Replace `MONGODB_URL` with your actual MongoDB connection string
   - If using MongoDB Atlas, the format is: `mongodb+srv://username:password@cluster.mongodb.net/buy2cash`

4. **Run the backend:**
   ```bash
   python main.py
   ```

## Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend-final
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

## Database Schema

The application expects the following MongoDB collections:

### Products Collection
```javascript
{
  _id: ObjectId,
  ProductName: String,
  imagelink: String,
  mrpPrice: Number,
  offerPrice: Number,
  category: String,
  subCategory: String,
  unit: String,
  isGstInclusive: Boolean,
  gst: Number,
  barcode: String,
  hsncode: String,
  stockQuantity: Number,
  status: String,
  availabilityStatus: String,
  type: String,
  createdAt: String,
  stage: String,
  ratings: Number,
  seller: String,
  image: String,
  commissions: Object
}
```

### Customers Collection
```javascript
{
  _id: ObjectId,
  customerName: String,
  email: String,
  phoneNumber: String,
  b2cWallet: Number,
  status: String,
  createdAt: String,
  signInType: String,
  profileImage: String,
  fcmToken: String,
  favoriteStore: String,
  favoriteCommunity: String,
  friends: Array,
  myChats: Array,
  Address: Array,
  google: Object
}
```

## Key Changes Made

1. **Backend:**
   - Replaced SQLAlchemy with Motor (async MongoDB driver)
   - Updated all database queries to use MongoDB syntax
   - Modified Pydantic schemas to match MongoDB document structure
   - Added proper error handling for MongoDB operations

2. **Frontend:**
   - Updated all interfaces to use MongoDB field names
   - Changed ID references from numbers to strings (MongoDB ObjectId)
   - Updated API calls to work with new backend structure
   - Modified data display to use new field names

## Features

- **Dashboard:** Overview of products, sales, and performance metrics
- **Products:** Product catalog management with search and filtering
- **Sales:** Sales analytics and transaction history
- **Users:** Customer management and loyalty tracking
- **Recommendations:** AI-powered product recommendations and substitutions

## API Endpoints

- `GET /products` - Get all products
- `GET /users` - Get all customers
- `GET /sales` - Get sales data
- `GET /recommendations` - Get basic recommendations
- `GET /ai-recommendations` - Get AI-powered recommendations
- `GET /reorder-recommendations` - Get reorder suggestions
- `GET /user-suggestions/{user_id}` - Get personalized suggestions
- `GET /substitution-suggestions/{product_id}` - Get product substitutions
- `GET /performance-benchmark` - Get performance metrics

## Troubleshooting

1. **MongoDB Connection Issues:**
   - Verify your MongoDB instance is running
   - Check your connection string format
   - Ensure network access if using cloud MongoDB

2. **Frontend API Errors:**
   - Verify the backend is running on the correct port
   - Check CORS settings if accessing from different domains
   - Update API URLs in frontend if needed

3. **Data Not Loading:**
   - Ensure your MongoDB collections have data
   - Check field names match the expected schema
   - Verify ObjectId format for IDs 