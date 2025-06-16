import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool, SerperDevTool

# API Key Setup
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
OPENAI_MODEL_NAME = os.getenv('OPENAI_MODEL_NAME', 'gpt-3.5-turbo') # Default to gpt-3.5-turbo

if not OPENAI_API_KEY:
    OPENAI_API_KEY = "YOUR_FALLBACK_OPENAI_KEY_HERE"
    print("WARNING: OPENAI_API_KEY not found in environment. Using fallback/dummy key. Real analysis will likely fail or be restricted.")
if not SERPER_API_KEY:
    SERPER_API_KEY = "YOUR_FALLBACK_SERPER_KEY_HERE"
    print("WARNING: SERPER_API_KEY not found in environment. Using fallback/dummy key. Real analysis will likely fail or be restricted.")

# Set environment variables for CrewAI and Langchain
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["SERPER_API_KEY"] = SERPER_API_KEY
os.environ["OPENAI_MODEL_NAME"] = OPENAI_MODEL_NAME

# Initialize LLM
default_llm = ChatOpenAI(model=os.environ["OPENAI_MODEL_NAME"], temperature=0.7)

# Tool Initialization
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# Agent Definitions
data_analyst_agent = Agent(
    role="Data Analyst",
    goal="Gather and analyze financial data for {stock_selection}, including performance, news, and market trends. "
         "Provide a detailed report on the stock's current standing and potential risks.",
    backstory="A meticulous Data Analyst with a knack for sifting through financial data, market trends, and news "
              "to provide actionable insights. Known for detailed reports and risk assessments.",
    verbose=True,
    allow_delegation=True,
    tools=[search_tool, scrape_tool],
    llm=default_llm
)

trading_strategy_agent = Agent(
    role="Trading Strategy Developer",
    goal="Develop a trading strategy for {stock_selection} based on the Data Analyst's report, user's risk tolerance "
         "({risk_tolerance}), and preferred trading strategy ({trading_strategy_preference}). "
         "Consider news impact ({news_impact_consideration}).",
    backstory="An experienced Trading Strategy Developer who creates tailored investment strategies. Balances risk "
              "and reward according to user preferences and market conditions.",
    verbose=True,
    allow_delegation=True,
    tools=[search_tool, scrape_tool],
    llm=default_llm
)

execution_agent = Agent(
    role="Execution Planner",
    goal="Create a detailed execution plan for the developed trading strategy for {stock_selection}, including entry/exit "
         "points and trade sizes, considering initial capital of {initial_capital}.",
    backstory="A precise Execution Planner who translates trading strategies into actionable steps. Focuses on minimizing "
              "slippage and maximizing efficiency.",
    verbose=True,
    allow_delegation=False,
    tools=[],
    llm=default_llm
)

risk_management_agent = Agent(
    role="Risk Management Specialist",
    goal="Assess and report on the risks associated with the trading strategy for {stock_selection}, "
         "considering {risk_tolerance} and {initial_capital}. Propose mitigation measures.",
    backstory="A cautious Risk Management Specialist who identifies potential pitfalls in trading strategies. "
              "Provides clear risk assessments and actionable mitigation advice.",
    verbose=True,
    allow_delegation=True,
    tools=[search_tool],
    llm=default_llm
)

# Task Definitions
data_analysis_task = Task(
    description=(
        "Gather and analyze comprehensive financial data for the stock: {stock_selection}. "
        "This includes historical performance, P/E ratios, EPS growth, revenue trends, and recent news articles. "
        "The analysis should also cover market sentiment and broader industry trends affecting the stock. "
        "Compile a detailed report summarizing the stock's current financial health, growth potential, and key risk factors."
    ),
    expected_output=(
        "A detailed report containing: "
        "1. Executive Summary of the stock's current standing. "
        "2. In-depth analysis of financial metrics (P/E, EPS, revenue trends). "
        "3. Summary of recent relevant news and its potential impact. "
        "4. Overview of market sentiment and industry trends. "
        "5. Identified key risks and opportunities."
    ),
    agent=data_analyst_agent,
)

strategy_development_task = Task(
    description=(
        "Based on the data analysis report for {stock_selection}, develop a specific trading strategy. "
        "This strategy must align with the user's stated risk tolerance of '{risk_tolerance}' and their "
        "preferred trading strategy type: '{trading_strategy_preference}'. "
        "Consider the impact of news ({news_impact_consideration}) as highlighted in the data analysis. "
        "The initial capital available is {initial_capital}."
    ),
    expected_output=(
        "A comprehensive trading strategy document detailing: "
        "1. Chosen strategy (e.g., value investing, growth investing, swing trading, day trading). "
        "2. Rationale for choosing the strategy based on data and user preferences. "
        "3. Specific financial instruments to be used (e.g., common stock, options if applicable). "
        "4. Justification of how news impact ({news_impact_consideration}) was factored into the strategy."
    ),
    agent=trading_strategy_agent,
)

execution_planning_task = Task(
    description=(
        "Create a detailed execution plan for the trading strategy developed for {stock_selection}. "
        "The plan should include specific entry points, target exit points (for profit-taking and stop-loss), "
        "and recommended trade sizes or position sizing rules, considering an initial capital of {initial_capital}. "
        "Outline the step-by-step process for executing the trades."
    ),
    expected_output=(
        "A detailed execution plan including: "
        "1. Recommended entry price range for {stock_selection}. "
        "2. Target exit price range (profit target). "
        "3. Stop-loss price level. "
        "4. Position sizing guidelines (e.g., percentage of {initial_capital} or number of shares). "
        "5. Step-by-step instructions for placing trades (e.g., order types to use)."
    ),
    agent=execution_agent,
)

risk_assessment_task = Task(
    description=(
        "Conduct a thorough risk assessment of the proposed trading strategy for {stock_selection}. "
        "Analyze potential risks including market risk, liquidity risk, and any specific risks related to the stock or strategy. "
        "The assessment must take into account the user's risk tolerance of '{risk_tolerance}' and initial capital {initial_capital}. "
        "Propose concrete mitigation measures for identified risks."
    ),
    expected_output=(
        "A comprehensive risk assessment report outlining: "
        "1. Identification and analysis of key risks (market, liquidity, stock-specific). "
        "2. Evaluation of risk level in context of user's '{risk_tolerance}' and {initial_capital}. "
        "3. Specific, actionable mitigation strategies for each identified risk (e.g., diversification, hedging techniques if applicable, adjusting position size)."
    ),
    agent=risk_management_agent,
)

# Crew Definition Function
def create_financial_crew():
    # Manager LLM is now also using the globally defined default_llm's model.
    manager_llm = ChatOpenAI(model=os.environ["OPENAI_MODEL_NAME"], temperature=0.7)
    financial_trading_crew = Crew(
        agents=[data_analyst_agent,
                trading_strategy_agent,
                execution_agent,
                risk_management_agent],
        tasks=[data_analysis_task,
               strategy_development_task,
               execution_planning_task,
               risk_assessment_task],
        manager_llm=manager_llm,
        process=Process.hierarchical,
        verbose=True
    )
    return financial_trading_crew

# Crew Execution Function
def run_crew_analysis(inputs_dict):
    if "YOUR_FALLBACK_OPENAI_KEY_HERE" in os.environ.get("OPENAI_API_KEY", "") or \
       "YOUR_FALLBACK_SERPER_KEY_HERE" in os.environ.get("SERPER_API_KEY", ""):
        print("WARNING: Attempting to run crew with fallback API keys.")
        return "Error: Agent execution requires valid OpenAI and Serper API keys. Please configure them in the environment."

    financial_crew = create_financial_crew()
    try:
        print(f"Starting crew kickoff with inputs: {inputs_dict}")
        result = financial_crew.kickoff(inputs=inputs_dict)
        return result
    except Exception as e:
        print(f"Error during crew kickoff: {e}")
        import traceback
        traceback.print_exc()
        return f"An error occurred during agent analysis: {str(e)}"

if __name__ == '__main__':
    print("Testing agent_logic.py module...")
    if "YOUR_FALLBACK_OPENAI_KEY_HERE" in os.environ.get("OPENAI_API_KEY", "") or \
       "YOUR_FALLBACK_SERPER_KEY_HERE" in os.environ.get("SERPER_API_KEY", ""):
        print("Skipping test run due to fallback API keys.")
    else:
        print("Attempting a test run with sample inputs (requires valid API keys)...")
        sample_inputs = {
            'stock_selection': 'TSLA',
            'initial_capital': '10000',
            'risk_tolerance': 'Medium',
            'trading_strategy_preference': 'Swing Trading',
            'news_impact_consideration': True
        }
        result = run_crew_analysis(sample_inputs)
        print("\nTest Run Result:")
        print(result)
