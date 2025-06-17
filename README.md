# Financial Agent with Real CrewAI Integration 🤖💰

A sophisticated web-based financial analysis application that uses **real CrewAI agents** to provide comprehensive stock analysis, trading strategies, execution plans, and risk assessments.

## 🆕 What's New: Real Agent Integration

This branch (`feat/financial-agent-ui-prototype`) now includes **real CrewAI agent integration**, making it a fully functional financial analysis tool powered by AI agents.

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

### 1. Automated Setup
```bash
./setup.sh
```

### 2. Manual Setup
```bash
# Create virtual environment
python3 -m venv financial_agent_env
source financial_agent_env/bin/activate

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
python app.py
```

### 5. Access the Application
Open your browser and go to: `http://localhost:8050/app/`

## 🎯 How to Use

### Login
- Enter any username/password (authentication is simulated)

### Stock Analysis
1. **Enter Stock Ticker** (e.g., AAPL, TSLA, GOOGL)
2. **Click "Fetch Stock Info"** to see basic stock information
3. **Configure Analysis Parameters:**
   - Initial Capital
   - Risk Tolerance (Low/Medium/High)
   - Trading Strategy Preference
   - News Impact Consideration

4. **Click "Run Analysis"** to start the multi-agent analysis

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
├── requirements.txt       # Python dependencies
├── setup.sh              # Automated setup script
├── .env.example          # Environment variables template
├── .env                  # Your API keys (create from .env.example)
└── README.md             # This file
```

## 🔧 Configuration Options

### Environment Variables
- `OPENAI_API_KEY`: Required for LLM functionality
- `SERPER_API_KEY`: Optional, enables web search capabilities
- `OPENAI_MODEL_NAME`: Default is `gpt-3.5-turbo`, can use `gpt-4` for better results

### Customization
- Modify agent roles and goals in `agent_logic.py`
- Adjust UI layout and styling in `app.py`
- Add new analysis parameters or visualizations

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

### Common Issues

**Import Errors**
```bash
# Ensure virtual environment is activated
source financial_agent_env/bin/activate
pip install -r requirements.txt
```

**API Key Errors**
- Verify keys are correctly set in `.env` file
- Check OpenAI account has sufficient credits
- Ensure Serper API key is valid (if using web search)

**Performance Issues**
- Use `gpt-3.5-turbo` for faster responses
- Reduce agent verbosity in `agent_logic.py`
- Consider caching for repeated analyses

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
