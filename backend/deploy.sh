#!/bin/bash

# Deployment script for FastAPI backend
# This script sets up the environment and runs the application

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    if [ -f "env.example" ]; then
        echo "📋 Creating .env from env.example template..."
        cp env.example .env
        echo "⚠️  Please edit .env file with your configuration before continuing!"
        exit 1
    else
        echo "📋 Please create .env file"
        exit 1
    fi
fi

# Run database connection test (optional)
echo "🔍 Testing database connection..."
python3 -c "from database import db; print('✅ Database connection successful')" || {
    echo "❌ Database connection failed!"
    exit 1
}

# Stop existing process if running
echo "🛑 Stopping existing processes..."
pkill -f "uvicorn main:app" || true
sleep 2

# Start the application
echo "🎯 Starting FastAPI application..."
nohup uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info \
    > app.log 2>&1 &

echo "✅ Deployment complete!"
echo "📝 Application is running on http://0.0.0.0:8000"
echo "📊 View logs with: tail -f app.log"
echo "🛑 Stop with: pkill -f 'uvicorn main:app'"

