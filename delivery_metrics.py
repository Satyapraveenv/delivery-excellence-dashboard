"""
Delivery Excellence Dashboard
Real-time program health monitoring for delivery leaders

A professional Dash/Plotly application that provides actionable insights into
program health using leading indicators:
- Sprint velocity trends
- Defect density tracking
- Resource utilization
- Customer satisfaction trajectories

Author: Satya Praveen Vemuri
License: MIT
Year: 2025
"""

import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
from data.sample_data import get_all_data

# ============================================================================
# CONFIGURATION & DESIGN CHOICES
# ============================================================================
# This dashboard uses a dark theme for extended viewing and reduced eye strain.
# All colors are chosen for clarity and professional presentation.
# Thresholds are set based on industry best practices for software delivery.

# Color palette - professional and accessible
COLOR_HEALTHY = '#10B981'      # Green - all is well
COLOR_WARNING = '#F59E0B'      # Amber - attention needed
COLOR_CRITICAL = '#EF4444'     # Red - immediate action required
COLOR_NEUTRAL = '#6B7280'      # Gray - neutral/info
COLOR_TEXT = '#F3F4F6'         # Light gray for text
COLOR_BG = '#111827'           # Dark background
COLOR_PANEL = '#1F2937'        # Slightly lighter panel background

# Performance thresholds (configurable)
VELOCITY_WARNING_VARIANCE = 15  # % variance from mean
VELOCITY_CRITICAL_VARIANCE = 25

DEFECT_DENSITY_WARNING = 4.0    # Bugs per 1000 LOC
DEFECT_DENSITY_CRITICAL = 6.0

UTILIZATION_WARNING = 85        # % capacity
UTILIZATION_CRITICAL = 95

CSAT_WARNING = 3.8              # Score out of 5
CSAT_CRITICAL = 3.5

# ============================================================================
# DATA LOADING
# ============================================================================

print("Initializing Delivery Excellence Dashboard...")
data = get_all_data()

velocity_df = data['velocity']
defects_df = data['defects']
resources_df = data['resources']
csat_df = data['csat']
burndown_df = data['burndown']

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_status_color(value, warning_threshold, critical_threshold, inverted=False):
    """
    Determine status color based on thresholds.

    Args:
        value: Current metric value
        warning_threshold: Threshold for warning state
        critical_threshold: Threshold for critical state
        inverted: If True, lower values are worse (for metrics like CSAT)

    Returns:
        Tuple of (color, status_text)
    """
    if not inverted:
        if value >= critical_threshold:
            return COLOR_CRITICAL, 'Critical'
        elif value >= warning_threshold:
            return COLOR_WARNING, 'Warning'
        else:
            return COLOR_HEALTHY, 'Healthy'
    else:
        if value <= critical_threshold:
            return COLOR_CRITICAL, 'Critical'
        elif value <= warning_threshold:
            return COLOR_WARNING, 'Warning'
        else:
            return COLOR_HEALTHY, 'Healthy'


def calculate_trend(series):
    """
    Calculate trend direction and magnitude.

    Returns:
        Tuple of (direction, magnitude) - direction in ['up', 'down', 'stable']
    """
    if len(series) < 2:
        return 'stable', 0

    recent = series.iloc[-3:].mean()
    previous = series.iloc[-6:-3].mean()

    if abs(recent - previous) < 0.5:
        return 'stable', 0

    change_pct = ((recent - previous) / previous * 100) if previous != 0 else 0
    direction = 'up' if recent > previous else 'down'

    return direction, abs(change_pct)


# ============================================================================
# CHART CREATION FUNCTIONS
# ============================================================================

def create_velocity_chart():
    """
    Create sprint velocity chart with trend line.

    Visual: Bar chart showing planned vs completed points with trend overlay.
    Design Thinking: Shows capacity predictability and team consistency.
    Leading Indicator: Stable velocity = predictable delivery.
    """
    fig = go.Figure()

    # Add planned points
    fig.add_trace(go.Bar(
        x=velocity_df['Sprint'],
        y=velocity_df['Planned_Points'],
        name='Planned Points',
        marker=dict(color=COLOR_NEUTRAL),
        opacity=0.6,
        hovertemplate='<b>%{x}</b><br>Planned: %{y} points<extra></extra>'
    ))

    # Add completed points
    fig.add_trace(go.Bar(
        x=velocity_df['Sprint'],
        y=velocity_df['Completed_Points'],
        name='Completed Points',
        marker=dict(color=COLOR_HEALTHY),
        hovertemplate='<b>%{x}</b><br>Completed: %{y} points<extra></extra>'
    ))

    # Add trend line
    z = np.polyfit(range(len(velocity_df)), velocity_df['Completed_Points'], 2)
    p = np.poly1d(z)
    trend_line = p(range(len(velocity_df)))

    fig.add_trace(go.Scatter(
        x=velocity_df['Sprint'],
        y=trend_line,
        name='Trend',
        mode='lines',
        line=dict(color='rgba(255, 255, 255, 0.5)', width=2, dash='dash'),
        hovertemplate='<b>Trend Line</b><br>Velocity: %{y:.0f}<extra></extra>'
    ))

    fig.update_layout(
        title='<b>Program Velocity</b><br><sub>Sprint capacity and delivery predictability</sub>',
        barmode='group',
        hovermode='x unified',
        template='plotly_dark',
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_PANEL,
        font=dict(color=COLOR_TEXT, size=12),
        margin=dict(l=50, r=50, t=100, b=50),
        xaxis=dict(title='Sprint', showgrid=False),
        yaxis=dict(title='Story Points', showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=450
    )

    return fig


def create_defect_density_chart():
    """
    Create defect density chart with status zones.

    Visual: Line chart showing defect density trend with color-coded zones.
    Design Thinking: Shows quality trajectory and risk trends.
    Leading Indicator: Rising defect density predicts customer issues 2-3 sprints ahead.
    """
    fig = go.Figure()

    # Add zone backgrounds
    fig.add_hrect(
        y0=DEFECT_DENSITY_CRITICAL, y1=8,
        annotation_text='Critical Zone', annotation_position='right',
        fillcolor=COLOR_CRITICAL, opacity=0.1, line_width=0
    )
    fig.add_hrect(
        y0=DEFECT_DENSITY_WARNING, y1=DEFECT_DENSITY_CRITICAL,
        annotation_text='Warning Zone', annotation_position='right',
        fillcolor=COLOR_WARNING, opacity=0.1, line_width=0
    )
    fig.add_hrect(
        y0=0, y1=DEFECT_DENSITY_WARNING,
        annotation_text='Healthy', annotation_position='right',
        fillcolor=COLOR_HEALTHY, opacity=0.1, line_width=0
    )

    # Add defect density line
    fig.add_trace(go.Scatter(
        x=defects_df['Sprint'],
        y=defects_df['Defect_Density'],
        mode='lines+markers',
        name='Defect Density',
        line=dict(color=COLOR_WARNING, width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Density: %{y:.2f} bugs/KLOC<extra></extra>'
    ))

    # Add threshold line
    fig.add_hline(
        y=DEFECT_DENSITY_WARNING,
        line_dash='dash',
        line_color=COLOR_WARNING,
        annotation_text='Warning Threshold',
        annotation_position='right'
    )

    fig.update_layout(
        title='<b>Defect Density Tracking</b><br><sub>Quality trend analysis (bugs per 1000 LOC)</sub>',
        hovermode='x unified',
        template='plotly_dark',
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_PANEL,
        font=dict(color=COLOR_TEXT, size=12),
        margin=dict(l=50, r=150, t=100, b=50),
        xaxis=dict(title='Sprint', showgrid=False),
        yaxis=dict(title='Bugs per 1000 LOC', showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        height=450
    )

    return fig


def create_resource_utilization_chart():
    """
    Create resource utilization heatmap.

    Visual: Horizontal bar chart showing team allocation with headroom indicators.
    Design Thinking: Shows capacity planning risks and team allocation imbalances.
    Leading Indicator: Teams at >90% utilization are one sick day away from slipping.
    """
    # Sort by utilization for better readability
    resources_sorted = resources_df.sort_values('Utilization_Percent', ascending=True)

    # Color bars based on utilization
    colors = []
    for util in resources_sorted['Utilization_Percent']:
        if util >= UTILIZATION_CRITICAL:
            colors.append(COLOR_CRITICAL)
        elif util >= UTILIZATION_WARNING:
            colors.append(COLOR_WARNING)
        else:
            colors.append(COLOR_HEALTHY)

    fig = go.Figure(data=[
        go.Bar(
            y=resources_sorted['Team'],
            x=resources_sorted['Utilization_Percent'],
            orientation='h',
            name='Utilization %',
            marker=dict(color=colors),
            text=resources_sorted['Utilization_Percent'].astype(str) + '%',
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Utilization: %{x:.1f}%<extra></extra>'
        )
    ])

    fig.update_layout(
        title='<b>Resource Utilization</b><br><sub>Team capacity and headroom analysis</sub>',
        barmode='group',
        hovermode='y unified',
        template='plotly_dark',
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_PANEL,
        font=dict(color=COLOR_TEXT, size=12),
        margin=dict(l=200, r=50, t=100, b=50),
        xaxis=dict(
            title='Utilization %',
            range=[0, 100],
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(showgrid=False),
        showlegend=False,
        height=400
    )

    return fig


def create_csat_chart():
    """
    Create CSAT trajectory chart.

    Visual: Line chart with trend showing customer satisfaction evolution.
    Design Thinking: Shows customer health and satisfaction momentum.
    Leading Indicator: Declining CSAT predicts churn and reduced retention.
    """
    fig = go.Figure()

    # Add CSAT trend
    fig.add_trace(go.Scatter(
        x=csat_df['Sprint'],
        y=csat_df['CSAT_Score'],
        mode='lines+markers',
        name='CSAT Score',
        line=dict(color=COLOR_HEALTHY, width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.2)',
        hovertemplate='<b>%{x}</b><br>CSAT: %{y:.2f}/5.0<extra></extra>'
    ))

    # Add critical threshold
    fig.add_hline(
        y=CSAT_CRITICAL,
        line_dash='dash',
        line_color=COLOR_CRITICAL,
        annotation_text='Critical Threshold',
        annotation_position='right'
    )

    # Add warning threshold
    fig.add_hline(
        y=CSAT_WARNING,
        line_dash='dash',
        line_color=COLOR_WARNING,
        annotation_text='Warning Threshold',
        annotation_position='right'
    )

    fig.update_layout(
        title='<b>Customer Satisfaction (CSAT)</b><br><sub>Trajectory and satisfaction momentum</sub>',
        hovermode='x unified',
        template='plotly_dark',
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_PANEL,
        font=dict(color=COLOR_TEXT, size=12),
        margin=dict(l=50, r=150, t=100, b=50),
        xaxis=dict(title='Sprint', showgrid=False),
        yaxis=dict(
            title='Score (out of 5.0)',
            range=[3, 5],
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        showlegend=True,
        height=450
    )

    return fig


def create_burndown_chart():
    """
    Create current sprint burndown chart.

    Visual: Area chart comparing ideal vs actual burndown.
    Design Thinking: Shows sprint execution health in real-time.
    Leading Indicator: Early sprint deviations predict sprint outcome.
    """
    fig = go.Figure()

    # Add ideal burndown
    fig.add_trace(go.Scatter(
        x=burndown_df['Day_Label'],
        y=burndown_df['Ideal_Remaining'],
        mode='lines',
        name='Ideal Burndown',
        line=dict(color=COLOR_NEUTRAL, width=2, dash='dash'),
        hovertemplate='<b>%{x}</b><br>Ideal: %{y:.0f} points<extra></extra>'
    ))

    # Add actual burndown
    fig.add_trace(go.Scatter(
        x=burndown_df['Day_Label'],
        y=burndown_df['Actual_Remaining'],
        mode='lines+markers',
        name='Actual Burndown',
        line=dict(color=COLOR_WARNING, width=3),
        marker=dict(size=6),
        fill='tonexty',
        fillcolor='rgba(245, 158, 11, 0.2)',
        hovertemplate='<b>%{x}</b><br>Actual: %{y:.0f} points<extra></extra>'
    ))

    fig.update_layout(
        title='<b>Current Sprint Burndown</b><br><sub>Real-time sprint execution tracking</sub>',
        hovermode='x unified',
        template='plotly_dark',
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_PANEL,
        font=dict(color=COLOR_TEXT, size=12),
        margin=dict(l=50, r=50, t=100, b=50),
        xaxis=dict(title='Sprint Day', showgrid=False),
        yaxis=dict(title='Points Remaining', showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=400
    )

    return fig


def create_metrics_summary():
    """
    Create summary metrics cards showing current health status.

    Returns:
        List of Dash html.Div components with key metrics
    """
    # Calculate latest metrics
    latest_velocity = velocity_df['Completed_Points'].iloc[-1]
    avg_velocity = velocity_df['Completed_Points'].mean()
    velocity_var = ((latest_velocity - avg_velocity) / avg_velocity * 100)

    latest_defects = defects_df['Defect_Density'].iloc[-1]
    defect_color, defect_status = get_status_color(
        latest_defects,
        DEFECT_DENSITY_WARNING,
        DEFECT_DENSITY_CRITICAL
    )

    latest_csat = csat_df['CSAT_Score'].iloc[-1]
    csat_color, csat_status = get_status_color(
        latest_csat,
        CSAT_WARNING,
        CSAT_CRITICAL,
        inverted=True
    )

    avg_utilization = resources_df['Utilization_Percent'].mean()
    util_color, util_status = get_status_color(
        avg_utilization,
        UTILIZATION_WARNING,
        UTILIZATION_CRITICAL
    )

    cards = [
        html.Div([
            html.Div('Current Velocity', style={'fontSize': '12px', 'color': COLOR_NEUTRAL}),
            html.Div(f"{int(latest_velocity)} pts", style={'fontSize': '28px', 'fontWeight': 'bold', 'color': COLOR_TEXT}),
            html.Div(f"{velocity_var:+.0f}% vs avg", style={'fontSize': '11px', 'color': COLOR_NEUTRAL})
        ], style={
            'padding': '20px',
            'backgroundColor': COLOR_PANEL,
            'borderRadius': '8px',
            'borderLeft': f'4px solid {COLOR_HEALTHY}'
        }),

        html.Div([
            html.Div('Defect Density', style={'fontSize': '12px', 'color': COLOR_NEUTRAL}),
            html.Div(f"{latest_defects:.2f}", style={'fontSize': '28px', 'fontWeight': 'bold', 'color': defect_color}),
            html.Div(f"{defect_status}", style={'fontSize': '11px', 'color': defect_color})
        ], style={
            'padding': '20px',
            'backgroundColor': COLOR_PANEL,
            'borderRadius': '8px',
            'borderLeft': f'4px solid {defect_color}'
        }),

        html.Div([
            html.Div('Customer CSAT', style={'fontSize': '12px', 'color': COLOR_NEUTRAL}),
            html.Div(f"{latest_csat:.2f}/5.0", style={'fontSize': '28px', 'fontWeight': 'bold', 'color': csat_color}),
            html.Div(f"{csat_status}", style={'fontSize': '11px', 'color': csat_color})
        ], style={
            'padding': '20px',
            'backgroundColor': COLOR_PANEL,
            'borderRadius': '8px',
            'borderLeft': f'4px solid {csat_color}'
        }),

        html.Div([
            html.Div('Avg Utilization', style={'fontSize': '12px', 'color': COLOR_NEUTRAL}),
            html.Div(f"{avg_utilization:.0f}%", style={'fontSize': '28px', 'fontWeight': 'bold', 'color': util_color}),
            html.Div(f"{util_status}", style={'fontSize': '11px', 'color': util_color})
        ], style={
            'padding': '20px',
            'backgroundColor': COLOR_PANEL,
            'borderRadius': '8px',
            'borderLeft': f'4px solid {util_color}'
        })
    ]

    return cards


# ============================================================================
# DASH APPLICATION SETUP
# ============================================================================

app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1('📊 Delivery Excellence Dashboard', style={'margin': 0, 'color': COLOR_TEXT}),
        html.P('Real-time program health monitoring for delivery leaders', style={
            'margin': '5px 0 0 0',
            'color': COLOR_NEUTRAL,
            'fontSize': '14px'
        })
    ], style={
        'padding': '30px',
        'backgroundColor': COLOR_PANEL,
        'borderBottom': f'2px solid {COLOR_HEALTHY}',
        'marginBottom': '30px'
    }),

    # Main container
    html.Div([
        # Metrics summary row
        html.Div([
            html.Div(create_metrics_summary(), style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
                'gap': '20px',
                'marginBottom': '30px'
            })
        ]),

        # Charts row 1
        html.Div([
            html.Div([
                dcc.Graph(figure=create_velocity_chart(), config={'responsive': True})
            ], style={'flex': 1}),
            html.Div([
                dcc.Graph(figure=create_defect_density_chart(), config={'responsive': True})
            ], style={'flex': 1})
        ], style={
            'display': 'flex',
            'gap': '20px',
            'marginBottom': '20px',
            'flexWrap': 'wrap'
        }),

        # Charts row 2
        html.Div([
            html.Div([
                dcc.Graph(figure=create_resource_utilization_chart(), config={'responsive': True})
            ], style={'flex': 1}),
            html.Div([
                dcc.Graph(figure=create_burndown_chart(), config={'responsive': True})
            ], style={'flex': 1})
        ], style={
            'display': 'flex',
            'gap': '20px',
            'marginBottom': '20px',
            'flexWrap': 'wrap'
        }),

        # CSAT chart - full width
        html.Div([
            dcc.Graph(figure=create_csat_chart(), config={'responsive': True})
        ], style={'marginBottom': '20px'}),

        # Footer
        html.Div([
            html.P([
                'Built with ',
                html.Span('Python', style={'color': COLOR_HEALTHY}),
                ', ',
                html.Span('Dash', style={'color': COLOR_HEALTHY}),
                ', and ',
                html.Span('Plotly', style={'color': COLOR_HEALTHY}),
                ' • ',
                'Last updated: ',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                ' UTC'
            ], style={
                'margin': 0,
                'color': COLOR_NEUTRAL,
                'fontSize': '12px',
                'textAlign': 'center'
            })
        ], style={
            'padding': '20px',
            'borderTop': f'1px solid rgba(255,255,255,0.1)',
            'marginTop': '30px'
        })

    ], style={
        'padding': '0 30px 30px 30px',
        'maxWidth': '1600px',
        'margin': '0 auto'
    })

], style={
    'backgroundColor': COLOR_BG,
    'color': COLOR_TEXT,
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    'minHeight': '100vh'
})

# ============================================================================
# RUN THE APP
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🚀 Delivery Excellence Dashboard")
    print("=" * 70)
    print("\n✓ Dashboard starting at http://localhost:8050")
    print("\nPress CTRL+C to stop the server.\n")
    print("=" * 70 + "\n")

    app.run_server(debug=True, host='127.0.0.1', port=8050)
