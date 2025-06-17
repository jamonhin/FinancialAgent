#!/bin/bash

# Setup script for the Financial Agent UI with Real CrewAI Integration

echo "🏗️  Setting up Financial Agent with Real CrewAI Integration..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "⬇️  Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✏️  Please edit .env file and add your API keys:"
    echo "    - OpenAI API Key: https://platform.openai.com/api-keys"
    echo "    - Serper API Key: https://serper.dev/"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: python app.py"
echo "3. Open: http://localhost:8050/app/"
echo ""
echo "Note: Without valid API keys, the agents will show an error message but the UI will still work."
