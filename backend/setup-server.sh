#!/bin/bash

# Server setup script for E2E instance
# Run this once on a fresh server to set up the environment

set -e

echo "🔧 Setting up Buy2Cash Backend Server..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip
echo "🐍 Installing Python..."
sudo apt-get install -y python3 python3-pip python3-venv git

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/buy2cash/backend
sudo chown -R $USER:$USER /opt/buy2cash

# Clone repository (if not already cloned)
if [ ! -d "/opt/buy2cash/.git" ]; then
    echo "📥 Cloning repository..."
    cd /opt/buy2cash
    git clone <your-repo-url> .
fi

# Create virtual environment
echo "🔧 Setting up virtual environment..."
cd /opt/buy2cash/backend
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration!"
fi

# Make deploy script executable
chmod +x deploy.sh

# Setup systemd service (optional)
read -p "Do you want to set up systemd service? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "⚙️  Setting up systemd service..."
    sudo cp buy2cash-api.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable buy2cash-api
    echo "✅ Systemd service configured. Start with: sudo systemctl start buy2cash-api"
fi

echo "✅ Server setup complete!"
echo "📝 Next steps:"
echo "   1. Edit /opt/buy2cash/backend/.env with your configuration"
echo "   2. Run ./deploy.sh to start the application"
echo "   3. Or use: sudo systemctl start buy2cash-api"

