# Financial Agent with Real CrewAI Integration 🤖💰

A sophisticated web-based financial analysis application that uses **real CrewAI agents** to provide comprehensive stock analysis, trading strategies, execution plans, and risk assessments. Features real-time Yahoo Finance data integration with enhanced charting capabilities.

## 🆕 What's New: Enhanced Real Data Integration

This branch (`feat/financial-agent-ui-prototype`) now includes:
- ✅ **Real CrewAI agent integration** with multi-agent collaboration
- ✅ **Live Yahoo Finance data** with enhanced charts and period selection
- ✅ **Multi-stock analysis** with unique color coding for each stock
- ✅ **Comprehensive debugging tools** for development and troubleshooting
- ✅ **Automated setup script** for quick installation

## 🤖 The Multi-Agent Team

The application employs a team of specialized AI agents:

1. **Data Analyst Agent** 📊
   - Analyzes financial data, market trends, and news
   - Provides detailed reports on stock performance and risks

2. **Trading Strategy Agent** 📈  
   - Develops tailored trading strategies based on user preferences
   - Considers risk tolerance and preferred trading style

3. **Execution Planner Agent** ⚡
   - Creates detailed execution plans with entry/exit points
   - Optimizes trade sizes based on available capital

4. **Risk Management Agent** 🛡️
   - Assesses risks and proposes mitigation strategies
   - Ensures alignment with user's risk tolerance

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))
- Serper API Key ([Get one here](https://serper.dev/)) - Optional but recommended for web search

### 🎯 Automated Setup (Recommended)

The easiest way to get started is using our automated setup script:

```bash
# Make setup script executable
chmod +x setup.sh

# Run automated setup
./setup.sh
```

**What the setup script does:**
- ✅ Creates virtual environment (`venv`)
- ✅ Activates the environment
- ✅ Installs all dependencies from `requirements.txt`
- ✅ Creates `.env` file from template
- ✅ Provides clear next steps

### 🔧 Manual Setup (Alternative)

If you prefer manual setup or need to troubleshoot:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. Configuration
Edit `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here
OPENAI_MODEL_NAME=gpt-3.5-turbo
```

### 4. Run the Application
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Start the application
python app.py
```

### 5. Access the Application
Open your browser and go to: `http://localhost:8050/app/`

## 🎯 How to Use

### Stock Chart Analysis
1. **Enter Stock Ticker(s)** (e.g., AAPL, TSLA, GOOGL or multiple: AAPL,MSFT,GOOGL)
2. **Select Time Period** from dropdown (1D, 5D, 1M, 3M, 6M, 1Y, 2Y, 5Y)
3. **Click "Fetch Stock Data"** to see real Yahoo Finance charts
4. **View Multi-Stock Analysis** with unique colors for each stock

### AI Agent Analysis
1. **Enter Stock Ticker** for detailed AI analysis
2. **Configure Analysis Parameters:**
   - Initial Capital
   - Risk Tolerance (Low/Medium/High)
   - Trading Strategy Preference
   - News Impact Consideration

3. **Click "Start AI Analysis"** to launch the multi-agent analysis

### Analysis Process
- The agents work collaboratively to analyze the stock
- Progress updates are shown in real-time
- Analysis typically takes 2-5 minutes depending on complexity
- Results include comprehensive financial analysis and actionable recommendations

## 🏗️ Technical Architecture

### Frontend
- **Dash & Plotly** for interactive web interface
- Real-time progress updates during agent execution
- Responsive design for desktop and mobile

### Backend  
- **CrewAI** for multi-agent orchestration
- **LangChain OpenAI** for LLM integration
- **Hierarchical agent process** for structured analysis
- **Background threading** for non-blocking UI

### Agent Workflow
```
Data Analyst → Trading Strategy → Execution Planner → Risk Management
     ↓              ↓                  ↓                 ↓
   Market Data   Strategy Plan     Execution Plan    Risk Report
```

## 📁 Project Structure

```
FinancialAgent/
├── app.py                 # Main Dash application with agent integration
├── agent_logic.py         # CrewAI agent definitions and orchestration
├── requirements.txt       # Python dependencies (updated with latest yfinance)
├── setup.sh              # 🆕 Automated setup script for easy installation
├── debug_threading.py     # 🆕 Threading debug tools for development
├── dev_commands.md        # 🆕 Comprehensive development documentation
├── .env.example          # Environment variables template
├── .env                  # Your API keys (create from .env.example)
├── assets/               # CSS and styling assets
│   └── modern-styles.css # Enhanced UI styling
└── README.md             # This file
```

## 🆕 New Features & Enhancements

### Real Yahoo Finance Integration
- **Live Data Fetching**: Real-time stock data from Yahoo Finance API
- **Period Selection**: Choose from 1D, 5D, 1M, 3M, 6M, 1Y, 2Y, 5Y
- **Multi-Stock Charts**: Compare multiple stocks with unique color coding
- **Enhanced Error Handling**: Graceful fallback to demo data if API fails
- **Volume Analysis**: Additional volume subplot for detailed analysis

### Development & Debugging Tools
- **setup.sh**: One-command automated environment setup
- **debug_threading.py**: Comprehensive threading monitoring and debugging
- **dev_commands.md**: Complete development workflow documentation
- **Environment Variables**: Debug controls for threading and simulation modes

### UI/UX Improvements
- **Responsive Layout**: Improved container overflow handling
- **Modern Styling**: Enhanced CSS with better visual hierarchy
- **Color Differentiation**: Unique colors for each stock in multi-stock analysis
- **Better Error Messages**: Clear feedback for various failure scenarios

## 🔧 Configuration Options

### Environment Variables
- `OPENAI_API_KEY`: Required for LLM functionality
- `SERPER_API_KEY`: Optional, enables web search capabilities
- `OPENAI_MODEL_NAME`: Default is `gpt-3.5-turbo`, can use `gpt-4` for better results

### Development/Debug Variables
- `DEBUG_THREADING`: Set to `true` to enable thread debugging output
- `DISABLE_BACKGROUND_THREADS`: Set to `true` for synchronous analysis (UI testing)
- `SIMULATE_ANALYSIS_RESULTS`: Set to `true` to use mock data for faster testing

### Using Debug Features
```bash
# Enable threading debug output
export DEBUG_THREADING=true

# Run in UI-friendly mode (no background threads)
export DISABLE_BACKGROUND_THREADS=true
export SIMULATE_ANALYSIS_RESULTS=true

# Start app with debugging
source venv/bin/activate
python app.py
```

### Customization
- Modify agent roles and goals in `agent_logic.py`
- Adjust UI layout and styling in `app.py`
- Add new analysis parameters or visualizations
- Customize stock data periods and chart types

## 🚨 Important Notes

### API Costs
- The application uses OpenAI's API which incurs costs
- Typical analysis costs $0.10-$0.50 depending on model and complexity
- Monitor usage through OpenAI dashboard

### Limitations
- Analysis quality depends on available public information
- Real-time data requires additional integrations
- Results are for educational/informational purposes only

### Security
- Never commit `.env` file to version control
- Keep API keys secure and rotate them regularly
- Use environment-specific configurations for production

## 🔄 Development Workflow

### Testing Without API Keys
The application will run without valid API keys but show error messages. This allows UI testing and development.

### Adding New Features
1. Modify agent definitions in `agent_logic.py`
2. Update UI components in `app.py`
3. Test with small examples to minimize API costs
4. Update documentation

## 🐛 Troubleshooting

### Quick Setup Issues

**Setup Script Not Executable**
```bash
chmod +x setup.sh
./setup.sh
```

**Virtual Environment Issues**
```bash
# If venv gets corrupted, recreate it
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Common Issues

**Import Errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Yahoo Finance Data Issues**
```bash
# Update to latest yfinance version
pip install --upgrade yfinance

# Check if yfinance is working
python -c "import yfinance as yf; print(yf.Ticker('AAPL').history(period='1d'))"
```

**API Key Errors**
- Verify keys are correctly set in `.env` file
- Check OpenAI account has sufficient credits
- Ensure Serper API key is valid (if using web search)

**Performance Issues**
- Use `gpt-3.5-turbo` for faster responses
- Reduce agent verbosity in `agent_logic.py`
- Consider caching for repeated analyses

**Threading/Hot Reload Issues**
```bash
# Use debug mode for development
export DEBUG_THREADING=true
export DISABLE_BACKGROUND_THREADS=true
python debug_threading.py  # Run threading diagnostics
```

### Getting Help
- Check `dev_commands.md` for detailed development workflows
- Use `debug_threading.py` for threading-related issues
- Monitor app logs with `tail -f app.log`

## 📈 Comparison: Before vs After

### Before (Placeholder Version)
- ❌ Static placeholder data
- ❌ No real analysis
- ❌ Simulated results only
- ✅ UI demonstration

### After (Real Agent Integration)
- ✅ Live AI agent analysis
- ✅ Real market insights
- ✅ Personalized recommendations
- ✅ Multi-agent collaboration
- ✅ Comprehensive financial reports

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test changes thoroughly
4. Update documentation
5. Submit a pull request

## 📜 License

This project is for educational and demonstration purposes. Please ensure compliance with API terms of service and financial regulations in your jurisdiction.

---

**Ready to analyze stocks with AI agents? Let's get started!** 🚀
