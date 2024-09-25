import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

app = Dash(__name__, use_pages=True, external_stylesheets = [dbc.themes.SLATE])

app.layout = html.Div([
    html.H2(children='Pacific Risk Tool for Resilience, Phase 2 (PARTneR-2)', style={'textAlign':'center'}),
    html.Div([
      html.Img(src="https://niwa.co.nz/sites/default/files/styles/portrait/public/PARTneR-2_partner%20logo%20panel.jpg"),
    ],style={'textAlign':'center'}),
    html.H3(children='Riskscape Dashboards', style={'textAlign':'center'}),
    html.Div([
        html.Span(
             dcc.Link("Sea Level Rise (SLR) | ", href="/slr", style={'textDecoration':'none'})
        ),
        html.Span(
             dcc.Link("Tropical Cyclone Rapid Exposure Forecast (REF) | ", href="/tcf", style={'textDecoration':'none'})
        ),
        html.Span(
             dcc.Link("Fluvial-Pluvial Flood (FPF) | ", href="/fpf", style={'textDecoration':'none'})
        ),
         html.Span(
             dcc.Link("Post Disaster Impact Estimation (PDIE)", href="/pdna", style={'textDecoration':'none'})
        ),
        html.Hr()
    ], style={'textAlign':'center'}),

     dash.page_container
    
], style={'font-family': 'Sans-Serif'})


if __name__ == '__main__':
    app.run(debug=True)

