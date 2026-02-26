#!/bin/bash

# PQIE Multi-Portal Server Startup Script
# Starts all PQIE services on different ports

echo "🌟 PQIE Multi-Portal Server Startup"
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements_pqie.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Start the multi-portal server
echo "🚀 Starting PQIE Multi-Portal Server..."
echo ""
echo "📱 Main Portal:     http://localhost:8080"
echo "🔗 Ethereum Portal: http://localhost:8081"
echo "⚙️ Admin Portal:     http://localhost:8082"
echo "📡 API Portal:       http://localhost:8083"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "=================================="

python3 pqie_multi_portal.py
