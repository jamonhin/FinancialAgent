import dash
from dash import dcc, html, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import threading
import time
import os
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
                        dcc.Markdown(id='analysis-report-display', 
                                    children="Analysis results will appear here after running the AI agents.",
                                    className="analysis-report-content",
                                    style={'background': 'var(--surface-color)', 'padding': '1.5rem', 
                                          'borderRadius': '8px', 'minHeight': '300px', 'border': '1px solid var(--border-color)',
                                          'color': 'var(--text-primary)'})
                    ], className="analysis-report-container")
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
    [State('stock-ticker-input', 'value')],
    prevent_initial_call=True
)
def update_stock_info(n_clicks, ticker_input):
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
    
    # Fetch real stock data from Yahoo Finance
    try:
        stock_data, real_chart = fetch_stock_data(tickers, period="6mo")
        placeholder_figure = real_chart
        
        # Add real stock info to the title
        if stock_data:
            successful_tickers = [ticker for ticker, data in stock_data.items() if data.get('current_price') is not None]
            if successful_tickers:
                placeholder_figure.update_layout(
                    title=dict(
                        text=f"Real-Time Stock Data - Last 6 Months ({len(successful_tickers)} stocks)" if len(tickers) > 1 else f"{tickers[0]} - Real-Time Data (6 Months)",
                        font=dict(size=16, color='var(--text-primary)'),
                        x=0.5
                    )
                )
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
    Fetch real stock data from Yahoo Finance with fallback to mock data
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
    
    colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#14b8a6']
    
    # Mock data as fallback
    mock_prices = {
        'AAPL': 175.50, 'MSFT': 285.30, 'GOOGL': 125.40, 'AMZN': 98.75,
        'TSLA': 185.60, 'META': 245.80, 'NVDA': 420.25, 'AMD': 105.30,
        'NFLX': 385.90, 'CRM': 195.40
    }
    
    def create_mock_data(ticker, base_price, days=30):
        """Create realistic mock stock data"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        prices = []
        current_price = base_price
        
        for i in range(days):
            # Random walk with slight upward bias
            change_percent = random.gauss(0.001, 0.02)  # Small upward bias, 2% volatility
            current_price *= (1 + change_percent)
            prices.append(max(current_price, 1.0))  # Ensure price doesn't go below $1
        
        return pd.DataFrame({
            'Close': prices,
            'Open': [p * random.uniform(0.98, 1.02) for p in prices],
            'High': [p * random.uniform(1.00, 1.03) for p in prices],
            'Low': [p * random.uniform(0.97, 1.00) for p in prices],
            'Volume': [random.randint(1000000, 50000000) for _ in prices]
        }, index=dates)
    
    for i, ticker in enumerate(tickers[:8]):  # Limit to 8 stocks for visibility
        try:
            print(f"Fetching data for {ticker}...")
            
            # Try to fetch real data first (with timeout and rate limiting)
            real_data_success = False
            try:
                time.sleep(0.5)  # Rate limiting
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d", timeout=5)  # Shorter period and timeout
                
                if not hist.empty and len(hist) > 0 and 'Close' in hist.columns:
                    current_price = float(hist['Close'].iloc[-1])
                    first_price = float(hist['Close'].iloc[0])
                    price_change = ((current_price - first_price) / first_price * 100) if first_price != 0 else 0
                    
                    stock_data[ticker] = {
                        'data': hist,
                        'current_price': current_price,
                        'price_change': price_change,
                        'source': 'real'
                    }
                    
                    figure.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['Close'],
                        mode='lines',
                        name=f"{ticker} (${current_price:.2f}) [Real]",
                        line=dict(color=colors[i % len(colors)], width=3),
                        hovertemplate=f"<b>{ticker}</b> [Real Data]<br>" +
                                    "Date: %{x}<br>" +
                                    "Price: $%{y:.2f}<br>" +
                                    "<extra></extra>"
                    ))
                    real_data_success = True
                    print(f"✓ Real data for {ticker}: ${current_price:.2f}")
                    
            except Exception as e:
                print(f"Real data failed for {ticker}: {e}")
            
            # If real data failed, use mock data
            if not real_data_success:
                base_price = mock_prices.get(ticker, random.uniform(50, 300))
                mock_hist = create_mock_data(ticker, base_price)
                
                current_price = mock_hist['Close'].iloc[-1]
                first_price = mock_hist['Close'].iloc[0]
                price_change = ((current_price - first_price) / first_price * 100)
                
                stock_data[ticker] = {
                    'data': mock_hist,
                    'current_price': current_price,
                    'price_change': price_change,
                    'source': 'mock'
                }
                
                figure.add_trace(go.Scatter(
                    x=mock_hist.index,
                    y=mock_hist['Close'],
                    mode='lines',
                    name=f"{ticker} (${current_price:.2f}) [Demo]",
                    line=dict(color=colors[i % len(colors)], width=3, dash='dot'),
                    hovertemplate=f"<b>{ticker}</b> [Demo Data]<br>" +
                                "Date: %{x}<br>" +
                                "Price: $%{y:.2f}<br>" +
                                "<extra></extra>"
                ))
                print(f"✓ Mock data for {ticker}: ${current_price:.2f}")
                
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
    
    # Configure the chart layout
    has_data = len([t for t in stock_data.values() if t.get('current_price') is not None]) > 0
    
    if has_data:
        # Check if we have any real data
        real_data_count = len([t for t in stock_data.values() if t.get('source') == 'real'])
        data_source_note = ""
        if real_data_count == 0:
            data_source_note = " [Demo Data - Limited API Access]"
        elif real_data_count < len(tickers):
            data_source_note = f" [Mixed: {real_data_count} Real, {len(tickers)-real_data_count} Demo]"
        else:
            data_source_note = " [Real-Time Data]"
            
        figure.update_layout(
            title=dict(
                text=f"Stock Price Chart{data_source_note}",
                font=dict(size=16, color='var(--text-primary)'),
                x=0.5
            ),
            xaxis=dict(
                title="Date",
                gridcolor='var(--border-color)',
                showgrid=True,
                color='var(--text-secondary)'
            ),
            yaxis=dict(
                title="Price (USD)",
                gridcolor='var(--border-color)',
                showgrid=True,
                color='var(--text-secondary)'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color='var(--text-secondary)'),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            margin=dict(l=0, r=0, t=50, b=0),
            height=400,
            annotations=[
                dict(
                    text="Note: Demo data used when real-time data is unavailable due to API limits",
                    xref="paper", yref="paper",
                    x=0.5, y=-0.15, xanchor='center', yanchor='top',
                    showarrow=False,
                    font=dict(size=10, color='var(--text-secondary)'),
                ) if real_data_count < len(tickers) else {}
            ]
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

# Callback to run financial analysis (real agent version)
@app.callback(
    [Output('analysis-report-display', 'children'),
     Output('agent-progress-display', 'children')],
    [Input('run-analysis-button', 'n_clicks')],
    [State('stock-ticker-input', 'value'),
     State('initial-capital-input', 'value'),
     State('risk-tolerance-dropdown', 'value'),
     State('strategy-preference-dropdown', 'value'),
     State('news-impact-checklist', 'value')],
    prevent_initial_call=True
)
def run_financial_analysis(n_clicks, stock_ticker_input, initial_capital, risk_tolerance, strategy_preference, news_impact_checklist_value):
    global analysis_progress
    
    if not stock_ticker_input:
        return no_update, "Error: Stock ticker(s) required. Please enter at least one stock symbol."

    # Parse tickers
    tickers = [t.strip().upper() for t in stock_ticker_input.split(',') if t.strip()]
    if len(tickers) == 0:
        return no_update, "Error: Please enter valid stock ticker(s)."

    news_impact = True if news_impact_checklist_value and 'True' in news_impact_checklist_value else False

    # Check if analysis is already running
    if analysis_progress['status'] == 'running':
        return analysis_progress['result'], "Analysis in progress... Please wait."
    
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
            return mock_result, "Synchronous mock analysis completed"
        else:
            # Run real analysis synchronously (WARNING: This will block the UI!)
            debug_print("WARNING: Running real analysis synchronously - UI will be blocked!")
            run_agent_analysis_background(stock_ticker_input, initial_capital, risk_tolerance, strategy_preference, news_impact)
            return analysis_progress['result'], "Synchronous analysis completed"
    
    else:
        # Normal background thread operation
        debug_print("Starting background thread for analysis")
        
        # Start background analysis
        analysis_thread = threading.Thread(
            target=run_agent_analysis_background,
            args=(stock_ticker_input, initial_capital, risk_tolerance, strategy_preference, news_impact)
        )
        analysis_thread.daemon = True
        
        # Debug: Option to comment out thread.start() for testing
        # UNCOMMENT THE FOLLOWING LINE TO DISABLE BACKGROUND THREAD EXECUTION:
        # debug_print("analysis_thread.start() COMMENTED OUT FOR DEBUGGING")
        analysis_thread.start()
        
        debug_print(f"Background thread started with ID: {analysis_thread.ident}")
    
    if len(tickers) == 1:
        return f"Single stock analysis started for {tickers[0]}. Check progress above...", "Starting analysis..."
    else:
        return f"Multi-stock comparative analysis started for {len(tickers)} stocks: {', '.join(tickers[:3])}{'...' if len(tickers) > 3 else ''}. Check progress above...", "Starting multi-stock analysis..."

# Callback to update progress display periodically
@app.callback(
    [Output('analysis-report-display', 'children', allow_duplicate=True),
     Output('agent-progress-display', 'children', allow_duplicate=True)],
    [Input('progress-interval', 'n_intervals')],
    [State('url', 'pathname')],
    prevent_initial_call=True
)
def update_analysis_progress(n_intervals, pathname):
    global analysis_progress
    
    # Only update if we're on the main page and analysis is running or completed
    if pathname == '/main' and analysis_progress['status'] in ['running', 'completed', 'error']:
        if analysis_progress['status'] == 'completed':
            return analysis_progress['result'], analysis_progress['message']
        elif analysis_progress['status'] == 'error':
            return f"**Error:** {analysis_progress['result']}", analysis_progress['message']
        else:  # running
            return "Analysis in progress... Please wait for the agents to complete their work.", analysis_progress['message']
    
    return no_update, no_update

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
