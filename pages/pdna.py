import dash
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

dash.register_page(__name__)

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

layout = html.Div([
  html.H3('Post Disaster Needs Assessment (PDNA)', style={'textAlign':'center'}),
  dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
  dcc.Graph(id='graph-content')
])

