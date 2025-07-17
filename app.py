import dash
from dash import dcc, html, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import threading
import concurrent.futures
import time
import signal
import sys
from functools import wraps

# Enhanced thread management and error handling
class SafeThreadManager:
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.active_futures = {}
        self.lock = threading.Lock()
    
    def submit_analysis(self, task_id, func, *args, **kwargs):
        """Submit analysis task with proper tracking and cleanup"""
        with self.lock:
            # Cancel any existing task with the same ID
            if task_id in self.active_futures:
                self.active_futures[task_id].cancel()
                debug_print(f"Cancelled existing task: {task_id}")
            
            # Submit new task
            future = self.executor.submit(func, *args, **kwargs)
            self.active_futures[task_id] = future
            debug_print(f"Submitted new task: {task_id}")
            return future
    
    def is_running(self, task_id):
        """Check if a task is currently running"""
        with self.lock:
            return task_id in self.active_futures and not self.active_futures[task_id].done()
    
    def cleanup_completed_tasks(self):
        """Clean up completed tasks"""
        with self.lock:
            completed_tasks = [task_id for task_id, future in self.active_futures.items() if future.done()]
            for task_id in completed_tasks:
                del self.active_futures[task_id]
            if completed_tasks:
                debug_print(f"Cleaned up {len(completed_tasks)} completed tasks")
    
    def shutdown(self):
        """Gracefully shutdown the thread pool"""
        debug_print("Shutting down thread manager...")
        self.executor.shutdown(wait=True)

# Global thread manager instance
thread_manager = SafeThreadManager()

def safe_callback(func):
    """Decorator to add error handling to callbacks"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"ERROR in callback {func.__name__}: {str(e)}")
            # Return safe defaults based on callback outputs
            if hasattr(func, '__annotations__'):
                return tuple(no_update for _ in range(len(func.__annotations__) - 1))
            return no_update
    return wrapper

def graceful_shutdown_handler(sig, frame):
    """Handle graceful shutdown"""
    print('\nGracefully shutting down Financial Agent...')
    thread_manager.shutdown()
    sys.exit(0)

# Register shutdown handlers
signal.signal(signal.SIGINT, graceful_shutdown_handler)
signal.signal(signal.SIGTERM, graceful_shutdown_handler)
import os
import random
# Using the working agent logic import
from agent_logic import run_crew_analysis
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Debug configuration for virtual environment issues
DEBUG_THREADING = os.getenv('DEBUG_THREADING', 'false').lower() == 'true'
DISABLE_BACKGROUND_THREADS = os.getenv('DISABLE_BACKGROUND_THREADS', 'false').lower() == 'true'
SIMULATE_ANALYSIS_RESULTS = os.getenv('SIMULATE_ANALYSIS_RESULTS', 'false').lower() == 'true'

def debug_print(message):
    """Print debug messages with thread information"""
    if DEBUG_THREADING:
        thread_id = threading.get_ident()
        thread_name = threading.current_thread().name
        print(f"[DEBUG] Thread {thread_id} ({thread_name}): {message}")

def get_active_threads_info():
    """Get information about active threads for debugging"""
    active_threads = threading.enumerate()
    return {
        'count': len(active_threads),
        'threads': [(t.name, t.ident, t.is_alive()) for t in active_threads]
    }

# Initialize Dash app with external stylesheets for modern look
external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
]

app = dash.Dash(__name__, 
                suppress_callback_exceptions=True, 
                external_stylesheets=external_stylesheets)

# Global variable to track analysis progress
analysis_progress = {
    'status': 'idle',
    'message': 'Ready to start analysis',
    'result': ''
}

# Global variable to store original and translated reports
report_storage = {
    'original': '',
    'translated': '',
    'current_language': 'en'  # 'en' for English, 'es' for Spanish
}

def translate_to_spanish(text):
    """Translate the analysis report to Spanish using OpenAI"""
    try:
        from langchain_openai import ChatOpenAI
        import os
        
        print(f"DEBUG: Starting translation for text of length: {len(text)}")
        
        # Get the OpenAI API key from environment
        openai_api_key = os.getenv('OPENAI_API_KEY')
        model_name = os.getenv('OPENAI_MODEL_NAME', 'gpt-3.5-turbo')  # Use gpt-3.5-turbo for faster and cheaper translation
        
        if not openai_api_key:
            print("DEBUG: OpenAI API key not found")
            return "Error: OpenAI API key not found. Translation requires a valid OpenAI API key."
        
        if not openai_api_key.startswith('sk-'):
            print("DEBUG: Invalid OpenAI API key format")
            return "Error: Invalid OpenAI API key format. Please check your API key."
        
        print(f"DEBUG: Using model: {model_name}")
        
        # Initialize the OpenAI client
        llm = ChatOpenAI(model=model_name, temperature=0.3, api_key=openai_api_key)
        
        # Create translation prompt
        translation_prompt = f"""
        You are a professional financial translator. Please translate the following financial analysis report from English to Spanish. 
        
        IMPORTANT INSTRUCTIONS:
        - Maintain all financial terminology accuracy
        - Keep all numbers, percentages, and monetary values exactly as they are
        - Preserve the markdown formatting (headers, bullets, etc.)
        - Use professional Spanish financial terminology
        - Keep the structure and organization of the report identical
        - Do not add any additional commentary or explanations
        
        TEXT TO TRANSLATE:
        {text}
        
        SPANISH TRANSLATION:
        """
        
        print("DEBUG: Sending translation request to OpenAI...")
        
        # Get the translation
        response = llm.invoke(translation_prompt)
        translated_text = response.content
        
        print(f"DEBUG: Translation completed. Result length: {len(translated_text)}")
        
        # Basic validation
        if not translated_text or len(translated_text) < 10:
            return "Error: Translation returned empty or too short result."
        
        return translated_text
        
    except Exception as e:
        error_msg = f"Translation Error: {str(e)}"
        print(f"DEBUG: Translation failed with error: {error_msg}")
        return error_msg

# Modern CSS styles - using external stylesheet with minimal inline overrides
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Financial AI Agent - Professional Stock Analysis</title>
        {%favicon%}
        {%css%}
        <style>
            /* Minimal theme initialization */
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 0;
                min-height: 100vh;
                transition: all 0.3s ease;
            }
            
            /* Container utilities */
            .modern-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            /* Dark theme toggle integration */
            .theme-indicator {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                background: var(--glass-bg);
                backdrop-filter: var(--backdrop-blur);
                border: 1px solid var(--border-color);
                border-radius: 50px;
                padding: 0.5rem 1rem;
                font-size: 0.9rem;
                color: var(--text-secondary);
                box-shadow: var(--shadow);
            }
        </style>
        <script>
            // Enhanced theme management
            function initTheme() {
                const savedTheme = localStorage.getItem('theme');
                const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                const theme = savedTheme || (systemDark ? 'dark' : 'light');
                
                console.log('Initializing theme:', theme);
                
                document.documentElement.setAttribute('data-theme', theme);
                document.body.className = theme === 'dark' ? 'dark-theme' : '';
                
                // Update theme indicator
                setTimeout(() => {
                    updateThemeIndicators(theme);
                }, 100);
            }
            
            function updateThemeIndicators(theme) {
                const indicator = document.querySelector('.theme-indicator');
                if (indicator) {
                    indicator.textContent = theme === 'dark' ? '🌙 Dark Mode' : '☀️ Light Mode';
                }
                
                // Update theme toggle icon
                const icon = document.getElementById('theme-icon');
                if (icon) {
                    icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
                }
            }
            
            function toggleTheme() {
                const current = document.documentElement.getAttribute('data-theme') || 'light';
                const newTheme = current === 'dark' ? 'light' : 'dark';
                
                console.log('Toggling theme from', current, 'to', newTheme);
                
                document.documentElement.setAttribute('data-theme', newTheme);
                document.body.className = newTheme === 'dark' ? 'dark-theme' : '';
                localStorage.setItem('theme', newTheme);
                
                updateThemeIndicators(newTheme);
                
                // Trigger any Dash callbacks that might be listening
                const button = document.getElementById('theme-toggle-btn');
                if (button && button.click) {
                    // Don't trigger infinite loop, just update the icon
                    updateThemeIndicators(newTheme);
                }
            }
            
            // Initialize theme on load
            document.addEventListener('DOMContentLoaded', initTheme);
            
            // Listen for system theme changes only if no manual preference is set
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    initTheme();
                }
            });
        </script>
    </head>
    <body>
        <div class="theme-indicator" onclick="toggleTheme()" style="cursor: pointer;">
            ☀️ Light Mode
        </div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Basic fallback body styling to prevent white screen
basic_body_style = {
    'fontFamily': 'Inter, Arial, sans-serif',
    'margin': '0',
    'padding': '20px',
    'backgroundColor': '#f8fafc',
    'color': '#1e293b',
    'minHeight': '100vh'
}

# Modern Login Page Layout
login_layout = html.Div([
    html.Div([
        html.Div([
            html.H1("🚀 Financial AI Agent", style={
                'textAlign': 'center', 
                'color': '#3b82f6', 
                'marginBottom': '1rem',
                'fontSize': '2rem'
            }),
            html.P("Professional Stock Analysis Powered by AI", style={
                'textAlign': 'center', 
                'color': '#64748b', 
                'marginBottom': '2rem'
            }),
            
            html.Div([
                html.Label("Username", style={'display': 'block', 'marginBottom': '0.5rem', 'fontWeight': 'bold'}),
                dcc.Input(
                    id='username-input', 
                    type='text', 
                    placeholder='Enter username',
                    style={
                        'width': '100%', 
                        'padding': '12px', 
                        'border': '1px solid #e2e8f0',
                        'borderRadius': '8px',
                        'marginBottom': '1rem'
                    }
                )
            ]),
            
            html.Div([
                html.Label("Password", style={'display': 'block', 'marginBottom': '0.5rem', 'fontWeight': 'bold'}),
                dcc.Input(
                    id='password-input', 
                    type='password', 
                    placeholder='Enter password',
                    style={
                        'width': '100%', 
                        'padding': '12px', 
                        'border': '1px solid #e2e8f0',
                        'borderRadius': '8px',
                        'marginBottom': '1rem'
                    }
                )
            ]),
            
            html.Button(
                "🔐 Sign In", 
                id='login-button', 
                n_clicks=0,
                style={
                    'width': '100%',
                    'padding': '12px',
                    'backgroundColor': '#3b82f6',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '8px',
                    'fontSize': '1rem',
                    'fontWeight': 'bold',
                    'cursor': 'pointer',
                    'marginBottom': '1rem'
                }
            ),
            
            html.Div(id='login-output'),
            
        ], style={
            'maxWidth': '400px',
            'margin': '5rem auto',
            'padding': '2rem',
            'backgroundColor': 'white',
            'borderRadius': '12px',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
            'border': '1px solid #e2e8f0'
        })
    ], style=basic_body_style)
], style={'minHeight': '100vh', 'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'})

# Modern Main Financial Analysis Page Layout
main_page_layout = html.Div([
    # Modern Navigation Bar
    html.Div([
        html.Div([
            html.Span([
                html.I(className="fas fa-chart-line", style={'marginRight': '0.5rem'}),
                "Financial AI Agent"
            ], className="nav-brand"),
            html.Div([
                html.Button([
                    html.I(id="theme-icon", className="fas fa-moon")
                ], 
                id="theme-toggle-btn",
                className="theme-toggle",
                title="Toggle dark/light mode"),
                html.Span("Welcome, Analyst", className="user-welcome"),
                dcc.Link([
                    html.I(className="fas fa-sign-out-alt", style={'marginRight': '0.5rem'}),
                    "Logout"
                ], href="/", className="logout-link")
            ], className="nav-controls")
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'maxWidth': '1400px', 'margin': '0 auto', 'padding': '0 2rem'})
    ], className="navbar"),

    # Main Content Container
    html.Div([
        # Header Section
        html.Div([
            html.H1([
                html.I(className="fas fa-robot", style={'marginRight': '1rem', 'color': 'rgba(255,255,255,0.9)'}),
                "AI-Powered Financial Analysis"
            ], className="header-title"),
            html.P("Multi-agent system for comprehensive stock analysis and trading strategies", className="header-subtitle")
        ], className="glass-card header-card"),

        # Main Grid Layout
        html.Div([
            # Left Column - Input Panel
            html.Div([
                html.Div([
                    html.H2([
                        html.I(className="fas fa-cog feature-icon", style={'marginRight': '0.5rem'}),
                        "Analysis Configuration"
                    ], className="section-title"),
                    
                    # Stock Input Section
                    html.Div([
                        html.Label("Stock Symbols", className="input-label"),
                        html.Div([
                            dcc.Input(
                                id='stock-ticker-input', 
                                type='text', 
                                placeholder='e.g., AAPL, TSLA, MSFT (separate with commas)',
                                className='modern-input',
                                style={'marginBottom': '0.5rem'}
                            ),
                            html.P([
                                html.I(className="fas fa-info-circle", style={'marginRight': '0.5rem', 'color': 'var(--primary-color)'}),
                                "Enter multiple stocks separated by commas for comparative analysis"
                            ], style={'fontSize': '0.85rem', 'color': 'var(--text-secondary)', 'margin': '0 0 1rem 0'}),
                            
                            # Chart Period Selector
                            html.Div([
                                html.Label("Chart Period", className="input-label"),
                                dcc.Dropdown(
                                    id='chart-period-dropdown',
                                    options=[
                                        {'label': '5 Days', 'value': '5d'},
                                        {'label': '1 Month', 'value': '1mo'},
                                        {'label': '3 Months', 'value': '3mo'},
                                        {'label': '6 Months', 'value': '6mo'},
                                        {'label': '1 Year', 'value': '1y'},
                                        {'label': '2 Years', 'value': '2y'}
                                    ],
                                    value='6mo',
                                    className='modern-dropdown',
                                    style={'marginBottom': '1rem'}
                                )
                            ]),
                            
                            html.Button([
                                html.I(className="fas fa-download", style={'marginRight': '0.5rem'}),
                                "Fetch Stock Info"
                            ], 
                                id='fetch-stock-info-button', 
                                className='modern-button button-secondary',
                                style={'width': '100%', 'marginBottom': '1.5rem'}
                            )
                        ])
                    ], className="input-group"),

                    # Parameters Section
                    html.Div([
                        html.Label("Initial Capital (USD)", className="input-label"),
                        dcc.Input(
                            id='initial-capital-input', 
                            type='number', 
                            placeholder='e.g., 10000',
                            className='modern-input'
                        )
                    ], className="input-group"),

                    html.Div([
                        html.Label("Risk Tolerance", className="input-label"),
                        dcc.Dropdown(
                            id='risk-tolerance-dropdown',
                            options=[
                                {'label': '🟢 Low Risk - Conservative', 'value': 'Low'},
                                {'label': '🟡 Medium Risk - Balanced', 'value': 'Medium'},
                                {'label': '🔴 High Risk - Aggressive', 'value': 'High'}
                            ],
                            value='Medium',
                            className='modern-input',
                            style={'marginBottom': '1rem'}
                        )
                    ], className="input-group"),

                    html.Div([
                        html.Label("Trading Strategy", className="input-label"),
                        dcc.Dropdown(
                            id='strategy-preference-dropdown',
                            options=[
                                {'label': '⚡ Day Trading - Short-term', 'value': 'Day Trading'},
                                {'label': '📈 Swing Trading - Medium-term', 'value': 'Swing Trading'},
                                {'label': '🏦 Long-term Investment', 'value': 'Long-term Investment'}
                            ],
                            value='Swing Trading',
                            className='modern-input',
                            style={'marginBottom': '1rem'}
                        )
                    ], className="input-group"),

                    html.Div([
                        dcc.Checklist(
                            id='news-impact-checklist',
                            options=[{'label': ' Include News Sentiment Analysis', 'value': 'True'}],
                            value=['True'],
                            style={'marginBottom': '1rem'},
                            labelStyle={'display': 'flex', 'alignItems': 'center', 'fontWeight': '500'}
                        )
                    ], className="input-group"),
                    
                    html.Div([
                        html.I(className="fas fa-info-circle", style={'marginRight': '0.5rem', 'color': 'var(--warning-color)'}),
                        "Real CrewAI agents will analyze the stock. Requires valid OpenAI API keys."
                    ], className="status-indicator status-warning", style={'marginBottom': '1rem'}),

                    html.Button([
                        html.I(className="fas fa-play", style={'marginRight': '0.5rem'}),
                        "Start Multi-Stock AI Analysis"
                    ], 
                        id='run-analysis-button', 
                        className='modern-button button-success',
                        style={'width': '100%', 'fontSize': '1.1rem', 'padding': '1rem'}
                    )
                ], className="glass-card")
            ], style={'gridColumn': '1'}),

            # Right Column - Results Panel
            html.Div([
                # Stock Information Card
                html.Div([
                    html.H2([
                        html.I(className="fas fa-chart-bar feature-icon", style={'marginRight': '0.5rem'}),
                        "Stock Information"
                    ], className="section-title"),
                    
                    html.Div(id='stock-name-display', 
                             children="Select a stock symbol and fetch information to begin analysis.",
                             style={'marginBottom': '1rem', 'color': 'var(--text-secondary)'}),
                    
                    dcc.Graph(id='stock-chart-graph', style={'marginBottom': '1rem'}),
                    
                    html.H3([
                        html.I(className="fas fa-newspaper", style={'marginRight': '0.5rem', 'color': 'var(--primary-color)'}),
                        "Recent News"
                    ], style={'marginBottom': '1rem', 'fontSize': '1.2rem'}),
                    
                    html.Div(id='news-feed-div', 
                             style={'height': '200px', 'overflowY': 'auto', 'background': 'var(--background-color)', 
                                   'padding': '1rem', 'borderRadius': '8px', 'border': '1px solid var(--border-color)'})
                ], className="glass-card"),

                # Analysis Results Card
                html.Div([
                    html.H2([
                        html.I(className="fas fa-brain feature-icon", style={'marginRight': '0.5rem'}),
                        "AI Agent Analysis"
                    ], className="section-title"),
                    
                    html.Div([
                        html.Div(id='agent-progress-display', 
                                 children="Ready to start analysis. Configure parameters and click 'Start AI Analysis'.",
                                 className="progress-container",
                                 style={'color': 'var(--text-primary)', 'background': 'var(--surface-elevated)'})
                    ]),
                    
                    html.Div([
                        html.Div([
                            html.Button(
                                [html.I(className="fas fa-language", style={'marginRight': '0.5rem'}), 
                                 "Translate to Spanish"],
                                id='translate-button',
                                className="translate-button",
                                style={'marginBottom': '1rem', 'display': 'none'},
                                n_clicks=0
                            ),
                            html.Button(
                                [html.I(className="fas fa-undo", style={'marginRight': '0.5rem'}), 
                                 "Show Original"],
                                id='show-original-button',
                                className="show-original-button",
                                style={'marginBottom': '1rem', 'marginLeft': '0.5rem', 'display': 'none'},
                                n_clicks=0
                            )
                        ], style={'textAlign': 'right'}),
                        
                        dcc.Markdown(id='analysis-report-display', 
                                    children="Analysis results will appear here after running the AI agents.",
                                    className="analysis-report-content",
                                    style={'background': 'var(--surface-color)', 'padding': '1.5rem', 
                                          'borderRadius': '8px', 'minHeight': '300px', 'border': '1px solid var(--border-color)',
                                          'color': 'var(--text-primary)'})
                    ], className="analysis-report-container", 
                       style={'overflowX': 'auto', 'wordBreak': 'break-word'})
                ], className="glass-card")
            ], style={'gridColumn': '2'})
        ], className="grid-layout")
    ], className="modern-container")
], style={'background': 'var(--background-color)', 'minHeight': '100vh'})

# App Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='progress-interval', interval=3000, n_intervals=0),  # Update every 3 seconds
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/main':
        return main_page_layout
    elif pathname == '/' or pathname is None:
        return login_layout
    return login_layout

@app.callback(
    Output('url', 'pathname'),
    [Input('login-button', 'n_clicks')],
    [State('username-input', 'value'),
     State('password-input', 'value')],
    prevent_initial_call=True
)
def login(n_clicks, username, password):
    if n_clicks > 0:
        return '/main'
    return no_update

@app.callback(
    [Output('stock-name-display', 'children'),
     Output('stock-chart-graph', 'figure'),
     Output('news-feed-div', 'children')],
    [Input('fetch-stock-info-button', 'n_clicks')],
    [State('stock-ticker-input', 'value'),
     State('chart-period-dropdown', 'value')],
    prevent_initial_call=True
)
def update_stock_info(n_clicks, ticker_input, chart_period):
    if not ticker_input:
        return "Please enter stock ticker(s).", {}, "No news available."

    # Parse multiple tickers
    tickers = [t.strip().upper() for t in ticker_input.split(',') if t.strip()]
    
    if len(tickers) == 0:
        return "Please enter valid stock ticker(s).", {}, "No news available."
    
    # Display info for multiple stocks
    if len(tickers) == 1:
        stock_name_text = html.Div([
            html.H3([
                html.I(className="fas fa-chart-line", style={'marginRight': '0.5rem', 'color': 'var(--success-color)'}),
                f"{tickers[0]}"
            ], style={'margin': '0', 'color': 'var(--primary-color)'}),
            html.P(f"Single stock analysis for {tickers[0]}", 
                   style={'margin': '0.5rem 0', 'color': 'var(--text-secondary)'})
        ])
    else:
        stock_name_text = html.Div([
            html.H3([
                html.I(className="fas fa-chart-bar", style={'marginRight': '0.5rem', 'color': 'var(--success-color)'}),
                "Multi-Stock Analysis"
            ], style={'margin': '0', 'color': 'var(--primary-color)'}),
            html.P(f"Comparative analysis for: {', '.join(tickers)}", 
                   style={'margin': '0.5rem 0', 'color': 'var(--text-secondary)'}),
            html.Div([
                html.Span(f"{len(tickers)} stocks selected", 
                         className="status-indicator status-success")
            ])
        ])
    
    # Fetch real stock data from Yahoo Finance with selected period
    try:
        stock_data, real_chart = fetch_stock_data(tickers, period=chart_period or "6mo")
        placeholder_figure = real_chart
        
        # The title is now handled within fetch_stock_data function
        
    except Exception as e:
        print(f"Error fetching real stock data: {e}")
        # Fallback to a simple message if Yahoo Finance fails
        placeholder_figure = go.Figure()
        placeholder_figure.add_annotation(
            text=f"Unable to fetch real-time data for {', '.join(tickers)}<br>Please check ticker symbols and try again",
            xref="paper", yref="paper", x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=14, color='var(--text-secondary)')
        )
        placeholder_figure.update_layout(
            title=dict(
                text="Stock Data Unavailable",
                font=dict(size=16, color='var(--text-primary)'),
                x=0.5
            ),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
    
    # Generate news for multiple stocks
    news_items = html.Div([
        html.Div([
            html.I(className="fas fa-newspaper", style={'marginRight': '0.5rem', 'color': 'var(--primary-color)'}),
            html.Strong(f"Market Update: {', '.join(tickers[:3])}{'...' if len(tickers) > 3 else ''}"),
            html.P("Multiple stocks showing strong performance in current market conditions.", 
                   style={'margin': '0.5rem 0', 'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
        ], style={'padding': '1rem', 'marginBottom': '1rem', 'background': 'white', 'borderRadius': '8px', 'border': '1px solid var(--border-color)'}),
        
        html.Div([
            html.I(className="fas fa-chart-up", style={'marginRight': '0.5rem', 'color': 'var(--success-color)'}),
            html.Strong("Sector Analysis Available"),
            html.P("Cross-sector comparison reveals interesting investment opportunities.", 
                   style={'margin': '0.5rem 0', 'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
        ], style={'padding': '1rem', 'marginBottom': '1rem', 'background': 'white', 'borderRadius': '8px', 'border': '1px solid var(--border-color)'}),
        
        html.Div([
            html.I(className="fas fa-balance-scale", style={'marginRight': '0.5rem', 'color': 'var(--warning-color)'}),
            html.Strong("Portfolio Diversification"),
            html.P(f"Analyzing {len(tickers)} stocks provides better risk distribution insights.", 
                   style={'margin': '0.5rem 0', 'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
        ], style={'padding': '1rem', 'background': 'white', 'borderRadius': '8px', 'border': '1px solid var(--border-color)'})
    ])
    
    return stock_name_text, placeholder_figure, news_items

# Utility function to fetch real stock data
def fetch_stock_data(tickers, period="6mo"):
    """
    Enhanced stock data fetching from Yahoo Finance with improved real-time data
    Args:
        tickers: List of stock symbols
        period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
    Returns:
        Dictionary with stock data and a Plotly figure
    """
    import time
    import random
    
    stock_data = {}
    figure = go.Figure()
    
    colors = [
        '#2563eb',  # Blue
        '#10b981',  # Green  
        '#f59e0b',  # Orange
        '#ef4444',  # Red
        '#8b5cf6',  # Purple
        '#06b6d4',  # Cyan
        '#ec4899',  # Pink
        '#14b8a6',  # Teal
        '#f97316',  # Orange-red
        '#84cc16',  # Lime
        '#6366f1',  # Indigo
        '#d946ef'   # Magenta
    ]
    
    # Mock data as fallback
    mock_prices = {
        'AAPL': 175.50, 'MSFT': 285.30, 'GOOGL': 125.40, 'AMZN': 98.75,
        'TSLA': 185.60, 'META': 245.80, 'NVDA': 420.25, 'AMD': 105.30,
        'NFLX': 385.90, 'CRM': 195.40, 'ORCL': 115.20, 'INTC': 45.80,
        'IBM': 135.60, 'SPY': 415.30, 'QQQ': 350.70, 'IWM': 185.40
    }
    
    def create_mock_data(ticker, base_price, days=180):  # Extended to 6 months of data
        """Create realistic mock stock data with better patterns"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        prices = []
        volumes = []
        current_price = base_price
        
        for i in range(days):
            # More realistic random walk with trends
            trend_factor = 0.0002 if i % 30 < 20 else -0.0001  # Monthly trend cycles
            change_percent = random.gauss(trend_factor, 0.018)  # Realistic volatility
            current_price *= (1 + change_percent)
            current_price = max(current_price, base_price * 0.5)  # Floor at 50% of original
            prices.append(current_price)
            
            # Realistic volume patterns
            base_volume = random.randint(1000000, 10000000)
            volume_mult = random.uniform(0.5, 2.0)
            volumes.append(int(base_volume * volume_mult))
        
        return pd.DataFrame({
            'Close': prices,
            'Open': [p * random.uniform(0.995, 1.005) for p in prices],
            'High': [p * random.uniform(1.002, 1.025) for p in prices],
            'Low': [p * random.uniform(0.975, 0.998) for p in prices],
            'Volume': volumes
        }, index=dates)
    
    def get_stock_info(ticker):
        """Get additional stock information"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                'longName': info.get('longName', ticker),
                'marketCap': info.get('marketCap'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'peRatio': info.get('trailingPE'),
                'dividendYield': info.get('dividendYield')
            }
        except:
            return {'longName': ticker}
    
    print(f"Fetching stock data for {len(tickers)} ticker(s): {', '.join(tickers)}")
    
    for i, ticker in enumerate(tickers[:8]):  # Limit to 8 stocks for visibility
        try:
            print(f"Processing {ticker} ({i+1}/{min(len(tickers), 8)})...")
            
            # Try to fetch real data with improved error handling
            real_data_success = False
            stock_info = {}
            
            try:
                time.sleep(0.3)  # Rate limiting for API
                stock = yf.Ticker(ticker)
                
                # Get stock info first
                stock_info = get_stock_info(ticker)
                
                # Fetch historical data with retry logic
                for attempt in range(2):  # Retry once if failed
                    try:
                        hist = stock.history(period=period, timeout=10)
                        if not hist.empty and len(hist) >= 2 and 'Close' in hist.columns:
                            # Validate data quality
                            if hist['Close'].isna().sum() / len(hist) < 0.5:  # Less than 50% missing data
                                break
                    except Exception as e:
                        print(f"Attempt {attempt + 1} failed for {ticker}: {e}")
                        if attempt == 0:
                            time.sleep(1)  # Wait before retry
                        else:
                            raise e
                
                if not hist.empty and len(hist) >= 2 and 'Close' in hist.columns:
                    # Clean the data
                    hist = hist.dropna()
                    
                    if len(hist) >= 2:
                        current_price = float(hist['Close'].iloc[-1])
                        first_price = float(hist['Close'].iloc[0])
                        price_change = ((current_price - first_price) / first_price * 100) if first_price != 0 else 0
                        
                        # Calculate additional metrics
                        volatility = hist['Close'].pct_change().std() * 100
                        avg_volume = hist['Volume'].mean() if 'Volume' in hist.columns else 0
                        
                        stock_data[ticker] = {
                            'data': hist,
                            'current_price': current_price,
                            'price_change': price_change,
                            'volatility': volatility,
                            'avg_volume': avg_volume,
                            'source': 'real',
                            'info': stock_info
                        }
                        
                        # Enhanced chart trace with unique colors for each stock
                        # Use unique color for each stock, not based on price change
                        stock_color = colors[i % len(colors)]
                        
                        figure.add_trace(go.Scatter(
                            x=hist.index,
                            y=hist['Close'],
                            mode='lines',
                            name=f"{ticker} ${current_price:.2f} ({price_change:+.1f}%)",
                            line=dict(color=stock_color, width=3),
                            hovertemplate=f"<b>{ticker}</b> - {stock_info.get('longName', ticker)}<br>" +
                                        "Date: %{x}<br>" +
                                        "Price: $%{y:.2f}<br>" +
                                        f"Change: {price_change:+.2f}%<br>" +
                                        "<extra></extra>"
                        ))
                        real_data_success = True
                        print(f"✓ Real data for {ticker}: ${current_price:.2f} ({price_change:+.1f}%)")
                    
            except Exception as e:
                print(f"Real data failed for {ticker}: {str(e)[:100]}...")
            
            # If real data failed, use enhanced mock data
            if not real_data_success:
                base_price = mock_prices.get(ticker, random.uniform(50, 300))
                
                # Determine period for mock data
                days_map = {'1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365}
                mock_days = days_map.get(period, 180)
                
                mock_hist = create_mock_data(ticker, base_price, mock_days)
                
                current_price = mock_hist['Close'].iloc[-1]
                first_price = mock_hist['Close'].iloc[0]
                price_change = ((current_price - first_price) / first_price * 100)
                volatility = mock_hist['Close'].pct_change().std() * 100
                
                stock_data[ticker] = {
                    'data': mock_hist,
                    'current_price': current_price,
                    'price_change': price_change,
                    'volatility': volatility,
                    'avg_volume': mock_hist['Volume'].mean(),
                    'source': 'mock',
                    'info': {'longName': f"{ticker} Corporation"}
                }
                
                figure.add_trace(go.Scatter(
                    x=mock_hist.index,
                    y=mock_hist['Close'],
                    mode='lines',
                    name=f"{ticker} ${current_price:.2f} [Demo]",
                    line=dict(color=colors[i % len(colors)], width=2, dash='dot'),
                    hovertemplate=f"<b>{ticker}</b> [Demo Data]<br>" +
                                "Date: %{x}<br>" +
                                "Price: $%{y:.2f}<br>" +
                                f"Change: {price_change:+.2f}%<br>" +
                                "<extra></extra>"
                ))
                print(f"✓ Mock data for {ticker}: ${current_price:.2f} ({price_change:+.1f}%)")
                
        except Exception as e:
            print(f"✗ Error processing {ticker}: {e}")
            # Last resort: simple static data
            stock_data[ticker] = {
                'data': None,
                'current_price': mock_prices.get(ticker, 100.0),
                'price_change': random.uniform(-5, 5),
                'source': 'static',
                'error': str(e)
            }
    
    # Configure the enhanced chart layout
    has_data = len([t for t in stock_data.values() if t.get('current_price') is not None]) > 0
    
    if has_data:
        # Check if we have any real data
        real_data_count = len([t for t in stock_data.values() if t.get('source') == 'real'])
        total_stocks = len([t for t in stock_data.values() if t.get('current_price') is not None])
        
        # Enhanced data source indicators
        if real_data_count == 0:
            data_source_note = " [Demo Data - API Unavailable]"
            title_color = '#f59e0b'  # Orange for demo
        elif real_data_count < total_stocks:
            data_source_note = f" [Mixed: {real_data_count} Real, {total_stocks-real_data_count} Demo]"
            title_color = '#8b5cf6'  # Purple for mixed
        else:
            data_source_note = " [Real-Time Data]"
            title_color = '#10b981'  # Green for all real
            
        # Calculate period display name
        period_names = {
            '1d': '1 Day', '5d': '5 Days', '1mo': '1 Month', 
            '3mo': '3 Months', '6mo': '6 Months', '1y': '1 Year'
        }
        period_display = period_names.get(period, period.upper())
            
        figure.update_layout(
            title=dict(
                text=f"Stock Price Analysis - {period_display}{data_source_note}",
                font=dict(size=18, color=title_color, family="Inter"),
                x=0.5,
                y=0.95
            ),
            xaxis=dict(
                title="Date",
                gridcolor='rgba(128,128,128,0.2)',
                showgrid=True,
                color='var(--text-secondary)',
                tickfont=dict(size=11),
                rangeslider=dict(visible=False),  # Remove range slider for cleaner look
                type='date'
            ),
            yaxis=dict(
                title="Price (USD)",
                gridcolor='rgba(128,128,128,0.2)',
                showgrid=True,
                color='var(--text-secondary)',
                tickfont=dict(size=11),
                tickformat='.2f'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color='var(--text-secondary)'),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.98,
                xanchor="left",
                x=1.02,
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='rgba(128,128,128,0.3)',
                borderwidth=1,
                font=dict(size=11)
            ),
            margin=dict(l=60, r=150, t=80, b=60),
            height=450,
            hovermode='x unified',  # Better hover interaction
            annotations=[]
        )
        
        # Add performance summary annotation
        if total_stocks > 0:
            real_stocks = [t for t in stock_data.values() if t.get('source') == 'real']
            if real_stocks:
                avg_change = sum(s['price_change'] for s in real_stocks) / len(real_stocks)
                change_color = '#10b981' if avg_change >= 0 else '#ef4444'
                
                figure.add_annotation(
                    text=f"Portfolio Avg: {avg_change:+.2f}% | Data Quality: {real_data_count}/{total_stocks} Real",
                    xref="paper", yref="paper",
                    x=0.02, y=0.02, xanchor='left', yanchor='bottom',
                    showarrow=False,
                    font=dict(size=12, color=change_color, family="Inter"),
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor=change_color,
                    borderwidth=1
                )
        
        # Add data source note for mixed data
        if real_data_count < total_stocks and real_data_count > 0:
            figure.add_annotation(
                text="⚠️ Some tickers show demo data due to API limitations",
                xref="paper", yref="paper",
                x=0.5, y=-0.12, xanchor='center', yanchor='top',
                showarrow=False,
                font=dict(size=10, color='var(--text-secondary)', style='italic'),
            )
    else:
        # Create error figure if no data was found
        figure.add_annotation(
            text=f"Unable to process: {', '.join(tickers)}<br>Please try again later",
            xref="paper", yref="paper", x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=14, color='var(--text-secondary)')
        )
        figure.update_layout(
            title=dict(
                text="Stock Data Processing Error",
                font=dict(size=16, color='var(--text-primary)'),
                x=0.5
            ),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
    
    return stock_data, figure
    
    return stock_data, figure

# Function to run agent analysis in background
def run_agent_analysis_background(stock_ticker_input, initial_capital, risk_tolerance, strategy_preference, news_impact):
    """Run the CrewAI agent analysis in a background thread"""
    global analysis_progress
    
    # Debug: Log thread start
    debug_print(f"BACKGROUND ANALYSIS STARTED - Ticker: {stock_ticker_input}")
    
    try:
        # Parse multiple tickers
        tickers = [t.strip().upper() for t in stock_ticker_input.split(',') if t.strip()]
        
        debug_print(f"Processing {len(tickers)} ticker(s): {tickers}")
        
        if len(tickers) == 1:
            analysis_progress['status'] = 'running'
            analysis_progress['message'] = html.Div([
                html.I(className="fas fa-cog fa-spin", style={'marginRight': '0.5rem', 'color': 'var(--primary-color)'}),
                f"Analyzing {tickers[0]}..."
            ], className="status-indicator status-processing")
        else:
            analysis_progress['status'] = 'running'
            analysis_progress['message'] = html.Div([
                html.I(className="fas fa-cogs fa-spin", style={'marginRight': '0.5rem', 'color': 'var(--primary-color)'}),
                f"Multi-stock analysis: {len(tickers)} stocks"
            ])
        
        # Check if we should simulate results instead of running real analysis
        if SIMULATE_ANALYSIS_RESULTS:
            debug_print("SIMULATION MODE: Using mock analysis results")
            time.sleep(2)  # Simulate some processing time
            result = f"""
# Simulated Analysis Results for {', '.join(tickers)}

## Investment Recommendation: MODERATE BUY

**Key Findings:**
- Current Price Analysis: Within normal trading range
- Technical Indicators: Mixed signals with slight bullish bias
- Risk Assessment: Medium risk profile suitable for balanced portfolios
- Market Sentiment: Neutral to positive

**Simulated Metrics:**
- Expected Return: 8-12% annually
- Risk Score: 6/10
- Volatility: Moderate
- Recommendation Strength: 75%

*Note: This is a simulated result for UI testing purposes.*
"""
        else:
            # Prepare inputs for the agent
            if len(tickers) == 1:
                # Single stock analysis
                inputs_dict = {
                    'stock_selection': tickers[0],
                    'initial_capital': str(initial_capital) if initial_capital else '10000',
                    'risk_tolerance': risk_tolerance,
                    'trading_strategy_preference': strategy_preference,
                    'news_impact_consideration': news_impact
                }
                
                analysis_progress['message'] = html.Div([
                    html.I(className="fas fa-brain fa-pulse", style={'marginRight': '0.5rem', 'color': 'var(--primary-color)'}),
                    f"AI agents analyzing {tickers[0]}..."
                ])
                
                debug_print(f"Running single stock analysis for {tickers[0]}")
                result = run_crew_analysis(inputs_dict)
                
            else:
                # Multi-stock comparative analysis
                analysis_progress['message'] = html.Div([
                    html.I(className="fas fa-brain fa-pulse", style={'marginRight': '0.5rem', 'color': 'var(--primary-color)'}),
                    f"Running comparative analysis on {len(tickers)} stocks..."
                ])
                
                # For multiple stocks, we'll create a comparative analysis
                stock_list = ', '.join(tickers)
                inputs_dict = {
                    'stock_selection': f"Portfolio comparison of {stock_list}",
                    'initial_capital': str(initial_capital) if initial_capital else '10000',
                    'risk_tolerance': risk_tolerance,
                    'trading_strategy_preference': strategy_preference,
                    'news_impact_consideration': news_impact
                }
                
                # Modify the analysis to include portfolio diversification insights
                inputs_dict['additional_context'] = f"Perform comparative analysis across {len(tickers)} stocks: {stock_list}. Focus on portfolio diversification, correlation analysis, and optimal allocation strategies."
                
                debug_print(f"Running multi-stock analysis for {len(tickers)} stocks")
                result = run_crew_analysis(inputs_dict)
        
        analysis_progress['status'] = 'completed'
        analysis_progress['message'] = html.Div([
            html.I(className="fas fa-check-circle", style={'marginRight': '0.5rem', 'color': 'var(--success-color)'}),
            f"Analysis completed for {len(tickers)} stock{'s' if len(tickers) > 1 else ''}!"
        ], className="status-indicator status-success")
        analysis_progress['result'] = result
        
        debug_print(f"BACKGROUND ANALYSIS COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        analysis_progress['status'] = 'error'
        analysis_progress['message'] = html.Div([
            html.I(className="fas fa-exclamation-triangle", style={'marginRight': '0.5rem', 'color': 'var(--error-color)'}),
            f"Analysis failed: {str(e)[:100]}..."
        ], className="status-indicator status-error")
        analysis_progress['result'] = f"**Error during analysis:** {str(e)}"
        
        debug_print(f"BACKGROUND ANALYSIS FAILED: {str(e)}")
    
    finally:
        # Debug: Log thread end and active threads
        debug_print(f"BACKGROUND ANALYSIS THREAD ENDING")
        if DEBUG_THREADING:
            threads_info = get_active_threads_info()
            debug_print(f"Active threads after analysis: {threads_info['count']}")
            for name, ident, is_alive in threads_info['threads']:
                debug_print(f"  - {name} (ID: {ident}, Alive: {is_alive})")

# Callback to run financial analysis (improved with thread management)
@app.callback(
    Output('run-analysis-button', 'disabled'),  # Only control the button state
    [Input('run-analysis-button', 'n_clicks')],
    [State('stock-ticker-input', 'value'),
     State('initial-capital-input', 'value'),
     State('risk-tolerance-dropdown', 'value'),
     State('strategy-preference-dropdown', 'value'),
     State('news-impact-checklist', 'value')],
    prevent_initial_call=True
)
@safe_callback
def run_financial_analysis(n_clicks, stock_ticker_input, initial_capital, risk_tolerance, strategy_preference, news_impact_checklist_value):
    global analysis_progress
    
    if not stock_ticker_input:
        return no_update

    # Parse tickers
    tickers = [t.strip().upper() for t in stock_ticker_input.split(',') if t.strip()]
    if len(tickers) == 0:
        return no_update

    news_impact = True if news_impact_checklist_value and 'True' in news_impact_checklist_value else False

    # Check if analysis is already running using thread manager
    if thread_manager.is_running('analysis_task'):
        return True  # Disable button while analysis is running
    
    # Clean up any completed tasks
    thread_manager.cleanup_completed_tasks()
    
    # Debug: Log callback start
    debug_print(f"ANALYSIS CALLBACK TRIGGERED - Tickers: {tickers}")
    
    # Reset progress
    analysis_progress = {
        'status': 'idle',
        'message': 'Ready to start analysis',
        'result': ''
    }
    
    # Check if background threads are disabled for debugging
    if DISABLE_BACKGROUND_THREADS:
        debug_print("BACKGROUND THREADS DISABLED - Running synchronous analysis")
        
        if SIMULATE_ANALYSIS_RESULTS:
            # Use simulation
            time.sleep(1)  # Brief delay to simulate processing
            mock_result = f"""
# Mock Analysis Results for {', '.join(tickers)}

## Investment Recommendation: MODERATE BUY (SYNC MODE)

**Key Findings:**
- This is a synchronous mock result for UI debugging
- Background threads are disabled
- All analysis runs in the main thread

**Mock Metrics:**
- Expected Return: 10% annually  
- Risk Score: 5/10
- Volatility: Low-Medium
- Recommendation: 80% confidence

*Note: Background threading disabled for debugging.*
"""
            analysis_progress['status'] = 'completed'
            analysis_progress['result'] = mock_result
            return False  # Re-enable button after analysis
        else:
            # Run real analysis synchronously (WARNING: This will block the UI!)
            debug_print("WARNING: Running real analysis synchronously - UI will be blocked!")
            run_agent_analysis_background(stock_ticker_input, initial_capital, risk_tolerance, strategy_preference, news_impact)
            return False  # Re-enable button after analysis
    
    else:
        # Use improved thread manager for background analysis
        debug_print("Starting managed background thread for analysis")
        
        # Submit analysis task to thread manager
        future = thread_manager.submit_analysis(
            'analysis_task',
            run_agent_analysis_background,
            stock_ticker_input, initial_capital, risk_tolerance, strategy_preference, news_impact
        )
        
        debug_print(f"Analysis task submitted to thread manager")
    
    # Start analysis and disable button temporarily
    if len(tickers) == 1:
        debug_print(f"Single stock analysis started for {tickers[0]}")
        return True  # Disable button while analysis is running
    else:
        debug_print(f"Multi-stock analysis started for {len(tickers)} stocks")
        return True  # Disable button while analysis is running

# Unified callback to handle all report-related updates (FIXED: No more allow_duplicate=True conflicts)
@app.callback(
    [Output('analysis-report-display', 'children'),
     Output('agent-progress-display', 'children'),
     Output('translate-button', 'style'),
     Output('show-original-button', 'style')],
    [Input('progress-interval', 'n_intervals'),
     Input('translate-button', 'n_clicks'),
     Input('show-original-button', 'n_clicks')],
    [State('url', 'pathname'),
     State('analysis-report-display', 'children')],
    prevent_initial_call=True
)
def unified_report_manager(n_intervals, translate_clicks, original_clicks, pathname, current_report):
    """
    Unified callback to prevent callback conflicts and circular dependencies.
    This replaces multiple callbacks with allow_duplicate=True that were causing crashes.
    """
    global analysis_progress, report_storage
    
    # Determine what triggered this callback
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update, no_update, no_update, no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Default button styles
    hide_style = {'marginBottom': '1rem', 'display': 'none'}
    translate_show_style = {'marginBottom': '1rem', 'display': 'inline-block'}
    original_show_style = {'marginBottom': '1rem', 'marginLeft': '0.5rem', 'display': 'inline-block'}
    
    try:
        # Handle progress interval updates
        if trigger_id == 'progress-interval':
            # Only update if we're on the main page and analysis is running or completed
            if pathname == '/main' and analysis_progress['status'] in ['running', 'completed', 'error']:
                if analysis_progress['status'] == 'completed':
                    # Store the original report if not already stored
                    if not report_storage['original']:
                        report_storage['original'] = analysis_progress['result']
                        report_storage['current_language'] = 'en'
                    
                    # Show the appropriate report based on current language
                    if report_storage['current_language'] == 'es' and report_storage['translated']:
                        # Show translated version if user is viewing translation
                        return report_storage['translated'], analysis_progress['message'], hide_style, original_show_style
                    else:
                        # Show original version
                        return analysis_progress['result'], analysis_progress['message'], translate_show_style, hide_style
                elif analysis_progress['status'] == 'error':
                    # Hide buttons on error
                    return f"**Error:** {analysis_progress['result']}", analysis_progress['message'], hide_style, hide_style
                else:  # running
                    # Hide buttons while running
                    return "Analysis in progress... Please wait for the agents to complete their work.", analysis_progress['message'], hide_style, hide_style
        
        # Handle translate button click
        elif trigger_id == 'translate-button':
            print(f"DEBUG: Translate button clicked. translate_clicks={translate_clicks}, original exists={bool(report_storage['original'])}, current_language={report_storage['current_language']}")
            
            if translate_clicks and translate_clicks > 0 and report_storage['original']:
                # Only translate if we have an original report and it's not already translated
                if report_storage['current_language'] == 'en':
                    print("DEBUG: Starting translation...")
                    
                    translated = translate_to_spanish(report_storage['original'])
                    print(f"DEBUG: Translation result length: {len(translated) if translated else 0}")
                    print(f"DEBUG: Translation starts with: {translated[:50] if translated else 'None'}...")
                    
                    if translated and not translated.startswith("Translation Error") and not translated.startswith("Error:"):
                        report_storage['translated'] = translated
                        report_storage['current_language'] = 'es'
                        
                        print("DEBUG: Translation successful, updating UI...")
                        
                        # Update button visibility
                        success_msg = html.Div([
                            html.I(className="fas fa-check-circle", style={'marginRight': '0.5rem', 'color': 'var(--success-color)'}),
                            "Translation completed successfully!"
                        ], className="status-indicator status-success")
                        
                        print(f"DEBUG: Returning translated content of length: {len(translated)}")
                        return translated, success_msg, hide_style, original_show_style
                    else:
                        # Translation failed, show error
                        print(f"DEBUG: Translation failed: {translated}")
                        error_msg = f"**Translation Failed:** {translated}"
                        error_display = html.Div([
                            html.I(className="fas fa-exclamation-triangle", style={'marginRight': '0.5rem', 'color': 'var(--error-color)'}),
                            "Translation failed. Please try again."
                        ], className="status-indicator status-error")
                        
                        return error_msg, error_display, translate_show_style, hide_style
                else:
                    # Already translated, show the existing translation
                    print(f"DEBUG: Already translated, showing existing translation of length: {len(report_storage['translated']) if report_storage['translated'] else 0}")
                    if report_storage['translated']:
                        return report_storage['translated'], analysis_progress['message'], hide_style, original_show_style
                    else:
                        print("DEBUG: No existing translation found, keeping current state")
                        return no_update, no_update, no_update, no_update
            else:
                # Debug: show why translation didn't trigger
                debug_msg = f"DEBUG: Translation not triggered. clicks={translate_clicks}, has_original={bool(report_storage['original'])}"
                print(debug_msg)
                return no_update, no_update, no_update, no_update
        
        # Handle show original button click
        elif trigger_id == 'show-original-button':
            if original_clicks and report_storage['original']:
                # Switch back to original report
                report_storage['current_language'] = 'en'
                
                # Update button visibility
                return report_storage['original'], analysis_progress['message'], translate_show_style, hide_style
        
        return no_update, no_update, no_update, no_update
        
    except Exception as e:
        # Safe error handling to prevent callback crashes
        print(f"Error in unified_report_manager: {str(e)}")
        return f"**Error:** An error occurred while updating the report.", "Error in report manager", hide_style, hide_style

# Theme toggle callback
app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            const current = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = current === 'dark' ? 'light' : 'dark';
            
            console.log('Dash callback: Toggling theme from', current, 'to', newTheme);
            
            document.documentElement.setAttribute('data-theme', newTheme);
            document.body.className = newTheme === 'dark' ? 'dark-theme' : '';
            localStorage.setItem('theme', newTheme);
            
            // Update theme indicator
            const indicator = document.querySelector('.theme-indicator');
            if (indicator) {
                indicator.textContent = newTheme === 'dark' ? '🌙 Dark Mode' : '☀️ Light Mode';
            }
            
            return newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
        
        // Initialize icon based on current theme
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        return currentTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
    """,
    Output('theme-icon', 'className'),
    Input('theme-toggle-btn', 'n_clicks'),
    prevent_initial_call=False
)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
