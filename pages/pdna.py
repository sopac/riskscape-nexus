import dash
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

dash.register_page(__name__)

layout = html.Div(
    [html.H3("Post Disaster Needs Assessment (PDNA)"), html.H5("In Development")],
    style={"textAlign": "center"},
)
