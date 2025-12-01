#!/bin/bash

# 🚀 INSTANT START - Run this to get everything working NOW!

clear

cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                    🚀 DAILICLE - INSTANT SETUP                          ║
║                  Your AI Article System in 5 Minutes                    ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

EOF

echo "This script will:"
echo "  1. ✓ Create virtual environment"
echo "  2. ✓ Install dependencies"
echo "  3. ✓ Set up configuration"
echo "  4. ✓ Test your setup"
echo "  5. ✓ Start the server"
echo ""
read -p "Press ENTER to continue (Ctrl+C to cancel)..."
echo ""

# Step 1: Create venv
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1/5: Creating virtual environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo "✓ Virtual environment created"
    else
        echo "✗ Failed to create virtual environment"
        exit 1
    fi
fi
echo ""

# Step 2: Activate and install
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2/5: Installing dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi
echo ""

# Step 3: Setup .env
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3/5: Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ".env" ]; then
    echo "✓ .env file exists"
    echo ""
    echo "⚠️  Configuration already exists. Do you want to:"
    echo "  1) Keep existing configuration"
    echo "  2) Reconfigure from scratch"
    read -p "Choice (1 or 2): " choice
    
    if [ "$choice" = "2" ]; then
        rm .env
        cp .env.example .env
        echo "✓ Created fresh .env file"
    fi
else
    cp .env.example .env
    echo "✓ Created .env file"
fi
echo ""

# Check if .env is configured
if grep -q "sk-your-openai-key-here" .env; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  IMPORTANT: Configure your API keys"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "You need to add your credentials to .env file:"
    echo ""
    echo "Required credentials:"
    echo "  • OPENAI_API_KEY - Get from: https://platform.openai.com/api-keys"
    echo "  • NOTION_API_KEY - Get from: https://www.notion.so/my-integrations"
    echo "  • NOTION_PARENT_PAGE_ID - From your Notion URL"
    echo "  • SMTP credentials - Gmail app password"
    echo ""
    echo "Do you want to:"
    echo "  1) Configure now (opens editor)"
    echo "  2) Configure later (manual)"
    echo "  3) Skip (for testing without API calls)"
    read -p "Choice (1, 2, or 3): " config_choice
    
    if [ "$config_choice" = "1" ]; then
        echo ""
        echo "Opening .env in editor..."
        echo "Add your API keys and save the file."
        echo ""
        read -p "Press ENTER when ready..."
        
        # Try different editors
        if command -v code &> /dev/null; then
            code .env
        elif command -v nano &> /dev/null; then
            nano .env
        elif command -v vim &> /dev/null; then
            vim .env
        else
            open .env
        fi
        
        echo ""
        read -p "Have you saved your API keys? (y/n): " saved
        if [ "$saved" != "y" ]; then
            echo "⚠️  Remember to configure .env before running the server!"
        fi
    elif [ "$config_choice" = "2" ]; then
        echo ""
        echo "✓ You can edit .env later with:"
        echo "  nano .env"
        echo "  # or"
        echo "  code .env"
    else
        echo "⚠️  Skipping configuration. Some features won't work without API keys."
    fi
    echo ""
fi

# Step 4: Create directories
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4/5: Setting up directories..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

mkdir -p articles
echo "✓ Created articles directory"
echo ""

# Step 5: Test or Run
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5/5: Next steps"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if grep -q "sk-proj" .env || grep -q "sk-" .env; then
    echo "✓ Configuration appears complete!"
    echo ""
    echo "What would you like to do?"
    echo "  1) Test configuration (recommended)"
    echo "  2) Start server now"
    echo "  3) Exit (start manually later)"
    read -p "Choice (1, 2, or 3): " action
    
    if [ "$action" = "1" ]; then
        echo ""
        echo "Running configuration tests..."
        echo ""
        python test_setup.py
        echo ""
        read -p "Start the server now? (y/n): " start
        if [ "$start" = "y" ]; then
            action="2"
        fi
    fi
    
    if [ "$action" = "2" ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🚀 Starting Dailicle Server..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Server will start at: http://localhost:8000"
        echo "API documentation: http://localhost:8000/docs"
        echo ""
        echo "Press Ctrl+C to stop the server"
        echo ""
        read -p "Press ENTER to start..."
        python main.py
    fi
else
    echo "⚠️  .env not configured yet"
    echo ""
    echo "Next steps:"
    echo "  1. Edit .env with your API keys:"
    echo "     nano .env"
    echo ""
    echo "  2. Test configuration:"
    echo "     source venv/bin/activate"
    echo "     python test_setup.py"
    echo ""
    echo "  3. Start server:"
    echo "     python main.py"
    echo ""
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Quick Reference"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To start server manually:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Test commands (in another terminal):"
echo "  curl http://localhost:8000/api/health"
echo "  curl -X POST http://localhost:8000/api/test-email"
echo ""
echo "Full documentation:"
echo "  • QUICKSTART.md - Step-by-step guide"
echo "  • DEPLOYMENT.md - Deploy to Railway/Render/Fly.io"
echo "  • README.md - Full features and architecture"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Setup complete! Happy article generating! 🎉"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
