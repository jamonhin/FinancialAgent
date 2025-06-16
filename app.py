import dash
from dash import dcc, html, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True, url_base_pathname='/app/')

# Login Page Layout
login_layout = html.Div([
    html.H1("Financial Analysis Agent Portal"),
    dcc.Input(id='username-input', type='text', placeholder='Username'),
    dcc.Input(id='password-input', type='password', placeholder='Password'),
    html.Button('Login', id='login-button', n_clicks=0),
    html.Div(id='login-output')
])

# Main Financial Analysis Page Layout
main_page_layout = html.Div([
    # Navigation Bar/Header
    html.Div([
        html.H1("Financial Analysis Agent Portal", style={'display': 'inline-block', 'marginRight': '20px'}),
        html.Div(id='welcome-user-message', children="Welcome, [Username]", style={'display': 'inline-block', 'marginRight': '20px'}),
        dcc.Link("Logout", href="/app/", style={'display': 'inline-block', 'padding': '5px 10px', 'border': '1px solid #007BFF', 'borderRadius': '5px', 'textDecoration': 'none'})
    ], style={'padding': '10px', 'borderBottom': '1px solid #eee'}),

    # Main page content container
    html.Div([
        # Left Column
        html.Div([
            # Input Section
            html.Div([
                html.Label("Stock Ticker:"),
                dcc.Input(id='stock-ticker-input', type='text', placeholder='E.g., AAPL', style={'marginBottom': '10px', 'width': '100%'}),
                html.Button("Fetch Stock Info", id='fetch-stock-info-button', style={'marginBottom': '20px', 'width': '100%'}),

                html.Label("Initial Capital (USD):"),
                dcc.Input(id='initial-capital-input', type='number', placeholder='E.g., 10000', style={'marginBottom': '10px', 'width': '100%'}),

                html.Label("Risk Tolerance:"),
                dcc.Dropdown(
                    id='risk-tolerance-dropdown',
                    options=[
                        {'label': 'Low', 'value': 'Low'},
                        {'label': 'Medium', 'value': 'Medium'},
                        {'label': 'High', 'value': 'High'}
                    ],
                    value='Medium',
                    style={'marginBottom': '10px', 'width': '100%'}
                ),

                html.Label("Trading Strategy Preference:"),
                dcc.Dropdown(
                    id='strategy-preference-dropdown',
                    options=[
                        {'label': 'Day Trading', 'value': 'Day Trading'},
                        {'label': 'Swing Trading', 'value': 'Swing Trading'},
                        {'label': 'Long-term Investment', 'value': 'Long-term Investment'}
                    ],
                    value='Day Trading',
                    style={'marginBottom': '10px', 'width': '100%'}
                ),

                dcc.Checklist(
                    id='news-impact-checklist',
                    options=[{'label': 'Consider News Impact', 'value': 'True'}],
                    value=['True'],
                    style={'marginBottom': '10px'}
                ),
                html.P( # This is the warning message for the current subtask
                    "Note: Analysis will be run with the provided inputs.",
                    style={'color': 'grey', 'fontSize': 'small', 'marginBottom': '5px'}
                ),
                html.Button("Run Analysis", id='run-analysis-button', style={'marginTop': '10px', 'width': '100%'})
            ], id='input-section', style={'marginBottom': '20px'}),

            # Stock Information Section
            html.Div([
                html.H3("Stock Information"),
                html.Div(id='stock-name-display', children="Stock details will appear here."),
                dcc.Graph(id='stock-chart-graph'),
                html.H4("Recent News"),
                html.Div(id='news-feed-div', style={'height': '200px', 'overflowY': 'scroll', 'border': '1px solid #ccc', 'padding': '10px'})
            ], id='stock-info-section')
        ], id='left-column', style={'width': '40%', 'padding': '10px', 'display': 'inline-block', 'verticalAlign': 'top'}),

        # Right Column
        html.Div([
            # Agent Status & Output Section
            html.Div([
                html.H3("Agent Analysis"),
                # The RED warning for synchronous call is REMOVED
                html.Div(id='agent-progress-display', children="Agent status will appear here."),
                dcc.Markdown(id='analysis-report-display', children="Analysis report will appear here.")
            ], id='output-section')
        ], id='right-column', style={'width': '58%', 'padding': '10px', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'display': 'flex'})
])

# App Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/app/main':
        return main_page_layout
    elif pathname == '/app/' or pathname == '/':
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
        return '/app/main'
    return no_update

@app.callback(
    [Output('stock-name-display', 'children'),
     Output('stock-chart-graph', 'figure'),
     Output('news-feed-div', 'children')],
    [Input('fetch-stock-info-button', 'n_clicks')],
    [State('stock-ticker-input', 'value')],
    prevent_initial_call=True
)
def update_stock_info(n_clicks, ticker):
    if not ticker:
        return "Please enter a stock ticker.", no_update, no_update

    stock_name_text = f"Displaying information for: {ticker.upper()}"
    placeholder_figure = go.Figure(data=[go.Scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 10], mode='lines+markers')])
    placeholder_figure.update_layout(title=f"{ticker.upper()} Stock Chart")
    news_items = [
        html.P(f"News item 1 for {ticker.upper()}."),
        html.P(f"News item 2 for {ticker.upper()}."),
        html.P(f"News item 3 for {ticker.upper()}.")
    ]
    return stock_name_text, placeholder_figure, news_items

# Callback to run financial analysis (placeholder version from Subtask 4)
# This is NOT the synchronous agent call version.
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
def run_financial_analysis(n_clicks, stock_ticker, initial_capital, risk_tolerance, strategy_preference, news_impact_checklist_value):
    if not stock_ticker: # Renamed from stock_ticker_val for consistency with this version
        return no_update, "Error: Stock Ticker is required. Please fetch stock info first."

    news_impact = True if news_impact_checklist_value and 'True' in news_impact_checklist_value else False # Renamed for consistency

    placeholder_report_md = f"# Financial Analysis for {stock_ticker.upper()}\n\n" # Renamed
    placeholder_report_md += f"**Initial Capital:** ${initial_capital:,.2f if initial_capital else 'N/A'}\n" # Renamed
    placeholder_report_md += f"**Risk Tolerance:** {risk_tolerance}\n" # Renamed
    placeholder_report_md += f"**Strategy Preference:** {strategy_preference}\n" # Renamed
    placeholder_report_md += f"**News Impact Considered:** {news_impact}\n\n"
    placeholder_report_md += "## Simulated Agent Report\n\n"
    placeholder_report_md += "This is a placeholder report demonstrating the data flow. Actual agent execution with detailed analysis, risk assessment, and financial instrument information will be implemented in subsequent steps.\n\n"
    placeholder_report_md += "### Key Findings (Placeholder):\n- **Overall Sentiment:** Positive.\n- **Projected Growth:** 5-7% (simulated).\n- **Key Risk Factor:** Market Volatility (simulated).\n"
    final_progress_message = "Analysis complete. Report generated below."
    return placeholder_report_md, final_progress_message

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
