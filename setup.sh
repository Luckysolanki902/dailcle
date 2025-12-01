#!/bin/bash

# Quick setup script for Dailicle
# This script helps you set up the project quickly

echo "=========================================="
echo "Dailicle Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - NOTION_API_KEY"
    echo "   - NOTION_PARENT_PAGE_ID"
    echo "   - SMTP credentials"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Create articles directory for local storage
mkdir -p articles
echo "✅ Created articles directory"
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file with your credentials:"
echo "   nano .env"
echo ""
echo "2. Run the server:"
echo "   python main.py"
echo "   # or"
echo "   uvicorn main:app --reload"
echo ""
echo "3. Test the API:"
echo "   curl http://localhost:8000/api/health"
echo ""
echo "4. Generate an article:"
echo "   curl -X POST http://localhost:8000/api/generate \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"topic_seed\": \"test topic\"}'"
echo ""
echo "5. Deploy to Railway/Render/Fly.io:"
echo "   See DEPLOYMENT.md for instructions"
echo ""
echo "=========================================="
