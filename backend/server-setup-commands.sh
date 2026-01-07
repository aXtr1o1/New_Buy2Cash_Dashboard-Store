#!/bin/bash
# Quick setup commands for E2E server
# Run these commands on your E2E server

echo "🔧 Installing required packages..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python-is-python3 git

echo "✅ Packages installed!"
echo ""
echo "Now you can continue with:"
echo "  cd /opt/buy2cash/New_Buy2Cash_Dashboard-Store/backend"
echo "  python3 -m venv venv"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"

