import dash
from dash import dcc, html, dash_table, Input, Output, ClientsideFunction
import plotly.graph_objs as go
import numpy as np
import pandas as pd
from datetime import datetime

# --- CONFIG & COLORS ---
CLR_BLUE = "#2563EB"
CLR_RED = "#EF4444"
CLR_GREEN = "#10B981"
CLR_SIDEBAR = "#EDF2F7"
LIMIT_H2O = 1.5

# Inisialisasi App
app = dash.Dash(__name__, title="SSD Production Monitoring")

# --- INITIAL DATA ---
history_h2o = [0.0] * 20
log_data = []

# --- LAYOUT ---
app.layout = html.Div(style={'backgroundColor': '#FFFFFF', 'fontFamily': 'Segoe UI, sans-serif', 'display': 'flex', 'height': '100vh', 'overflow': 'hidden'}, children=[
    
    # Elemen Tersembunyi untuk Memicu Suara (JS)
    html.Div(id="audio-trigger", style={"display": "none"}),

    # 1. SIDEBAR
    html.Div(style={'width': '250px', 'backgroundColor': CLR_SIDEBAR, 'padding': '20px', 'display': 'flex', 'flexDirection': 'column'}, children=[
        html.H1("SSD", style={'textAlign': 'center', 'fontWeight': 'bold', 'color': '#374151', 'fontSize': '40px', 'margin': '10px 0'}),
        html.P("CHECK COUNTER H2O", style={'textAlign': 'center', 'fontWeight': 'bold', 'color': CLR_BLUE, 'fontSize': '12px'}),
        html.Button("Monitoring Live", style={'backgroundColor': CLR_BLUE, 'color': 'white', 'border': 'none', 'padding': '12px', 'margin': '10px 0', 'borderRadius': '5px', 'fontWeight': 'bold', 'cursor': 'pointer'}),
        html.Button("Dashboard Analytics", style={'backgroundColor': '#F59E0B', 'color': 'white', 'border': 'none', 'padding': '12px', 'margin': '5px 0', 'borderRadius': '5px', 'fontWeight': 'bold', 'cursor': 'pointer'}),
    ]),

    # 2. MAIN CONTENT
    html.Div(style={'flex': '1', 'padding': '20px', 'overflowY': 'auto'}, children=[
        
        # Header / Clock
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}, children=[
            html.Span("SSD - PRODUCTION MONITORING SYSTEM", style={'color': '#D1D5DB', 'fontWeight': 'bold', 'fontSize': '12px'}),
            html.Span(id="live-clock", style={'fontWeight': 'bold', 'color': '#4B5563'})
        ]),

        # KPI CARDS
        html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
            # Card Moisture
            html.Div(style={'flex': '1', 'border': '1px solid #D1D5DB', 'padding': '20px', 'borderRadius': '8px'}, children=[
                html.Label("PERSEN MOISTURE", style={'color': '#6B7280', 'fontWeight': 'bold'}),
                html.H2(id="kpi-moisture", children="0.00 %", style={'fontSize': '40px', 'margin': '10px 0'})
            ]),
            # Card Status
            html.Div(id="status-box", style={'flex': '1', 'padding': '20px', 'borderRadius': '8px', 'color': 'white', 'backgroundColor': CLR_GREEN}, children=[
                html.Label("STATUS", style={'fontWeight': 'bold'}),
                html.H2(id="kpi-status", children="AMAN", style={'fontSize': '40px', 'margin': '10px 0'})
            ]),
        ]),

        # GRAPHS ROW
        html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
            html.Div(style={'flex': '1', 'border': '1px solid #D1D5DB', 'borderRadius': '8px', 'padding': '10px'}, children=[
                html.B("Trend Kelembapan H2O (%)"),
                dcc.Graph(id='trend-graph', config={'displayModeBar': False})
            ]),
            html.Div(style={'flex': '1', 'border': '1px solid #D1D5DB', 'borderRadius': '8px', 'padding': '10px'}, children=[
                html.B("NIR Spectral Signature"),
                dcc.Graph(id='nir-graph', config={'displayModeBar': False})
            ]),
        ]),

        # LOG TABLE
        html.Div(style={'border': '1px solid #D1D5DB', 'borderRadius': '8px', 'padding': '10px'}, children=[
            html.B("DATA LOG HISTORY"),
            dash_table.DataTable(
                id='log-table',
                columns=[
                    {"name": "TIMESTAMP", "id": "ts"},
                    {"name": "TYPE", "id": "type"},
                    {"name": "SOURCE", "id": "src"},
                    {"name": "MESSAGE", "id": "msg"},
                    {"name": "STATUS", "id": "stat"}
                ],
                style_header={'backgroundColor': '#F3F4F6', 'fontWeight': 'bold'},
                style_cell={'textAlign': 'left', 'padding': '10px', 'fontFamily': 'Segoe UI'},
                style_data_conditional=[{
                    'if': {'filter_query': '{type} eq "ALARM"'},
                    'color': CLR_RED, 'fontWeight': 'bold'
                }],
                page_size=10
            )
        ]),

        dcc.Interval(id='interval-component', interval=2000, n_intervals=0)
    ])
])

# --- CALLBACKS (Server-side untuk Data) ---
@app.callback(
    [Output('live-clock', 'children'),
     Output('kpi-moisture', 'children'),
     Output('kpi-moisture', 'style'),
     Output('kpi-status', 'children'),
     Output('status-box', 'style'),
     Output('trend-graph', 'figure'),
     Output('nir-graph', 'figure'),
     Output('log-table', 'data')],
    [Input('interval-component', 'n_intervals')]
)
def update_metrics(n):
    global history_h2o, log_data
    
    now = datetime.now()
    val = round(0.85 + np.random.uniform(-0.3, 0.9), 2)
    
    history_h2o.append(val)
    history_h2o = history_h2o[-20:]

    is_alarm = val > LIMIT_H2O
    status_text = "BAHAYA" if is_alarm else "AMAN"
    status_bg = CLR_RED if is_alarm else CLR_GREEN
    moist_color = CLR_RED if is_alarm else "#1F2937"

    new_log = {
        "ts": now.strftime("%H:%M:%S"),
        "type": "ALARM" if is_alarm else "NORMAL",
        "src": "SENSOR_H20_09",
        "msg": f"Moisture Level: {val}%" + (" (CRITICAL)" if is_alarm else ""),
        "stat": "ACTIVE" if is_alarm else "OK"
    }
    log_data.insert(0, new_log)
    log_data = log_data[:50]

    fig_trend = go.Figure(data=[go.Scatter(y=history_h2o, mode='lines+markers', line=dict(color=CLR_BLUE))])
    fig_trend.add_hline(y=LIMIT_H2O, line_dash="dash", line_color=CLR_RED)
    fig_trend.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#F9FAFB')

    x_nir = np.linspace(340, 850, 100)
    y_nir = np.random.normal(1200, 100, 100) + 5000 * np.exp(-((x_nir - 760)**2) / 1000)
    fig_nir = go.Figure(data=[go.Scatter(x=x_nir, y=y_nir, mode='lines', line=dict(color=CLR_GREEN))])
    fig_nir.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#F9FAFB')

    return (
        now.strftime("%A, %d %B %Y | %H:%M:%S"),
        f"{val:.2f} %",
        {'color': moist_color, 'fontSize': '40px', 'margin': '10px 0'},
        status_text,
        {'flex': '1', 'padding': '20px', 'borderRadius': '8px', 'backgroundColor': status_bg, 'color': 'white'},
        fig_trend,
        fig_nir,
        log_data
    )

# --- CALLBACKS (Clientside untuk Suara) ---
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='play_beep'
    ),
    Output("audio-trigger", "children"),
    Input("kpi-moisture", "children")
)

if __name__ == '__main__':
    app.run(debug=True, port=8050)