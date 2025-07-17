# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Financial Agent application that uses CrewAI multi-agent systems to provide AI-powered stock analysis and trading recommendations. The app features real-time Yahoo Finance data integration, interactive Dash web interface, and comprehensive multi-agent collaboration for financial analysis.

## Key Development Commands

### Environment Setup
```bash
# Automated setup (recommended)
chmod +x setup.sh
./setup.sh

# Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the Application
```bash
# Start the web application
source venv/bin/activate
python app.py

# Start in background
nohup python app.py > app.log 2>&1 &

# Stop the application
pkill -f "python app.py"

# Check application status
lsof -i :8050
```

### Development & Testing
```bash
# Test translation functionality
python test_translation.py

# Run with debug features
export DEBUG_THREADING=true
export SIMULATE_ANALYSIS_RESULTS=true
python app.py

# Thread debugging and monitoring
python debug_threading.py
```

### Server Management (using setup.sh)
```bash
./setup.sh install   # Install dependencies
./setup.sh start     # Start server
./setup.sh stop      # Stop server
./setup.sh restart   # Restart server
./setup.sh status    # Check server status
./setup.sh debug     # Start in debug mode
```

## Architecture Overview

### Core Components
- **app.py**: Main Dash web application with UI, callbacks, and Yahoo Finance integration
- **agent_logic.py**: CrewAI multi-agent system with 4 specialized financial agents
- **setup.sh**: Automated setup and server management script
- **debug_threading.py**: Development debugging tools for thread management

### Multi-Agent System
The application uses 4 specialized CrewAI agents:
1. **Data Analyst Agent**: Analyzes financial data and market trends
2. **Trading Strategy Agent**: Develops personalized trading strategies
3. **Execution Planner Agent**: Creates detailed execution plans with entry/exit points
4. **Risk Management Agent**: Assesses risks and proposes mitigation strategies

### Data Flow
1. User inputs stock symbols and parameters via Dash UI
2. Real-time data fetched from Yahoo Finance API (yfinance)
3. Background thread executes CrewAI multi-agent analysis
4. Results displayed in interactive charts and comprehensive reports

## Configuration

### Required Environment Variables (.env file)
```env
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here  # Optional
OPENAI_MODEL_NAME=gpt-3.5-turbo  # Default model
```

### Debug Environment Variables
```env
DEBUG_THREADING=true  # Enable thread debugging output
DISABLE_BACKGROUND_THREADS=true  # Run analysis synchronously
SIMULATE_ANALYSIS_RESULTS=true  # Use mock data for testing
```

## Key Features

### Real-time Data Integration
- Yahoo Finance API integration with yfinance library
- Multi-stock analysis with unique color coding
- Interactive Plotly charts with period selection (1D, 5D, 1M, 3M, 6M, 1Y, 2Y)
- Graceful fallback to mock data when APIs fail

### Thread Management
- SafeThreadManager class for robust background processing
- Comprehensive thread debugging and monitoring tools
- Graceful shutdown handling with signal management

### UI Features
- Modern responsive design with CSS variables
- Dark/light theme support
- Real-time progress updates during analysis
- Multi-language support (English/Spanish translation)

## Common Development Tasks

### Adding New Agents
1. Define new agent in agent_logic.py
2. Create corresponding task definition
3. Update crew creation function
4. Test with sample inputs

### Modifying UI Components
1. Update layout in app.py (look for `main_page_layout`)
2. Add new callbacks for interactivity
3. Update CSS in assets/modern-styles.css if needed
4. Test with different screen sizes

### Debugging Threading Issues
1. Set DEBUG_THREADING=true in environment
2. Run debug_threading.py for comprehensive monitoring
3. Check app.log for detailed thread lifecycle information
4. Use DISABLE_BACKGROUND_THREADS=true for synchronous testing

## Dependencies

### Core Dependencies
- `dash==3.0.4` - Web framework
- `plotly==6.1.2` - Interactive charts
- `crewai==0.130.0` - Multi-agent AI framework
- `langchain-openai==0.3.23` - OpenAI integration
- `yfinance==0.2.63` - Yahoo Finance data

### Development Dependencies
- `python-dotenv==1.1.0` - Environment variables
- `pandas==2.2.3` - Data manipulation

## Important Notes

### API Usage
- OpenAI API key required for AI agents to function
- Typical analysis costs $0.10-$0.50 per run
- Serper API key optional but recommended for web search

### Thread Safety
- Application uses ThreadPoolExecutor for background processing
- SafeThreadManager handles task lifecycle and cleanup
- Debug tools available for monitoring thread behavior

### Error Handling
- Graceful fallback to mock data when APIs fail
- Comprehensive error messages for API issues
- Client-side error handling for UI stability

## File Structure Reference

```
FinancialAgent/
├── app.py                    # Main Dash application
├── agent_logic.py            # CrewAI multi-agent system
├── setup.sh                  # Server management script
├── debug_threading.py        # Development debugging tools
├── test_translation.py       # Translation functionality test
├── requirements.txt          # Python dependencies
├── dev_commands.md          # Development command reference
├── PROJECT_ARCHITECTURE.md  # Detailed architecture documentation
├── README.md                # User documentation
├── assets/
│   └── modern-styles.css    # UI styling
├── venv/                    # Virtual environment
└── .env                     # Environment variables (not tracked)
```

## Troubleshooting

### Common Issues
- **Import errors**: Ensure virtual environment is activated
- **API key errors**: Check .env file configuration
- **Port conflicts**: Use `lsof -i :8050` to check port usage
- **Threading issues**: Enable DEBUG_THREADING and check logs

### Development Mode
For UI development without API calls:
```bash
export DISABLE_BACKGROUND_THREADS=true
export SIMULATE_ANALYSIS_RESULTS=true
python app.py
```

This allows rapid UI iteration without waiting for AI analysis or consuming API credits.