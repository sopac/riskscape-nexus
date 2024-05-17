import dash
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

dash.register_page(__name__)

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

layout = html.Div([
  html.H3('Fluvial-Pluvial Flood (FPF)', style={'textAlign':'center'}),
  dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
  dcc.Graph(id='graph-content')
])

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.country==value]
    return px.line(dff, x='year', y='pop')