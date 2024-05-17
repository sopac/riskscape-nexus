import dash
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

dash.register_page(__name__)

layout = html.Div([
    html.H3('Tropical Cyclone Forecast (TCF)', style={'textAlign':'center'}),
    
])