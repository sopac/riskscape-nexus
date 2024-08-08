import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import geopandas as gpd
import pandas as pd
import dash_leaflet as dl
import dash_leaflet.express as dlx
import json
from collections import OrderedDict
import plotly.graph_objects as go
import io

dash.register_page(__name__)

project_name = "pdna"

############################### LOAD DATA AND PREPARE DATA ###############################

#  load all the geojsons first  #

#load cyclone track
gdf_cyclone_track = gpd.read_file(
    "data/" + project_name + "/" + "cyclone-track.geojson"
)

#load damaged buildings
gdf_damaged_buildings = gpd.read_file(
    "data/" + project_name + "/" + "damaged-buildings.geojson"
)

#load damaged roads
gdf_damaged_roads = gpd.read_file(
    "data/" + project_name + "/" + "damaged-roads.geojson"
)

#load exposure by cluster
gdf_exposure_by_cluster = gpd.read_file(
    "data/" + project_name + "/" + "exposure-by-cluster.geojson"
)

#load regional impacts
gdf_regional_impacts = gpd.read_file(
    "data/" + project_name + "/" + "regional-impacts.geojson"
)


#  load all the csv files next  #

#load impact by asset type
df_impact_by_asset_type = pd.read_csv(
    "data/" + project_name + "/" + "impact-by-asset-type.csv"
)

#load national summary
df_national_summary = pd.read_csv(
    "data/" + project_name + "/" + "national-summary.csv"
)

#load regional summary
df_regional_summary = pd.read_csv(
    "data/" + project_name + "/" + "regional-summary.csv"
)

############################### DROPDOWN SELECTION CONFIGURATION ###############################

# create region list for region selection dropdown
regions = gdf_regional_impacts["Region.Region"].tolist()
regions = [region for region in regions if region is not None]
regions.sort()
regions = ['All regions'] + regions

############################### MAP COMPONENT ###############################

# mapinfo
colorscale = ["red", "yellow", "green", "blue", "purple"]  # rainbow



############################### MAP FEATURE INFO BOX ###############################

#### in development ######




############################### DASHBOARD LAYOUT ###############################
layout = html.Div(
    [
        dbc.Row(
            dbc.Col(
                html.H3("Post Disaster Needs Assessment (PDNA)", style={"textAlign": "center", "color": "white"})
            ),
            style={"backgroundColor": "#CCCCFF", "padding": "10px"}  # Periwinkle background for the header row
        ),
        dbc.Row(
            [
                # Column for Dropdowns
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.Label("Country:", style={"color": "black"}),
                                dcc.Dropdown(
                                    options=[
                                        {"label": "Tonga", "value": "Tonga"},
                                        {"label": "Samoa", "value": "Samoa"},
                                        {"label": "Cook Islands", "value": "Cook Islands"},
                                        {"label": "Vanuatu", "value": "Vanuatu"},
                                    ],
                                    value="Vanuatu",
                                    id="country-select",
                                    style={"width": "100%", "backgroundColor": "#ffffff", "color": "black"}  # Dropdown background color
                                ),
                            ],
                            style={"marginBottom": "10px"}
                        ),
                        html.Div(
                            [
                                html.Label("Hazard:", style={"color": "black"}),
                                dcc.Dropdown(
                                    options=[
                                        {"label": "Wind", "value": "Wind"},
                                        {"label": "Coastal Inundation", "value": "Coastal Inundation"},
                                        {"label": "Cyclone Track", "value": "Cyclone Track"},
                                        {"label": "Storm Surge", "value": "Storm Surge"},
                                    ],
                                    value="Cyclone Track",
                                    id="hazard-select",
                                    style={"width": "100%", "backgroundColor": "#ffffff", "color": "black"}  # Dropdown background color
                                ),
                            ],
                            style={"marginBottom": "10px"}
                        ),
                        html.Div(
                            [
                                html.Label("Cluster:", style={"color": "black"}),
                                dcc.Dropdown(
                                    options=[
                                        {"label": "Agriculture", "value": "Agriculture"},
                                        {"label": "Social", "value": "Social"},
                                        {"label": "Health", "value": "Health"},
                                    ],
                                    value="Agriculture",
                                    id="cluster-select",
                                    style={"width": "100%", "backgroundColor": "#ffffff", "color": "black"}  # Dropdown background color
                                ),
                            ],
                            style={"marginBottom": "10px"}
                        ),
                        html.Div(
                            [
                                html.Label("Aggregation:", style={"color": "black"}),
                                dcc.Dropdown(
                                    options=[
                                        {"label": "National", "value": "National"},
                                        {"label": "Regional", "value": "Regional"},
                                        {"label": "Provincial", "value": "Provincial"},
                                        {"label": "District", "value": "District"},
                                    ],
                                    value="National",
                                    id="aggregation-select",
                                    style={"width": "100%", "backgroundColor": "#ffffff", "color": "black"}  # Dropdown background color
                                ),
                            ]
                        ),
                    ],
                    width=2,  # Width for dropdowns column
                    style={"paddingRight": "10px"}  # Add some spacing on the right side
                ),
                # Column for Map, Graphs, and Text Boxes
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dl.Map(
                                        [
                                            dl.TileLayer(),
                                            dl.GeoJSON(
                                                data=json.loads(
                                                   gdf_cyclone_track["geometry"].to_json()
                                                ),
                                                id="pdna-map",
                                                zoomToBounds=True,
                                                zoomToBoundsOnClick=True,
                                                style=dict(
                                                    weight=2,
                                                    opacity=1,
                                                    color="red",
                                                    fillOpacity=0.5,
                                                    colorscale=colorscale,
                                                ),
                                            ),
                                        ],
                                        zoom=6,
                                        style={"height": "60vh"},
                                        center=(
                                            gdf_cyclone_track.dissolve().centroid.y.values[0].item(),
                                            gdf_cyclone_track.dissolve().centroid.x.values[0].item(),
                                        ),
                                    ),
                                    width=6  # Width for the map column
                                ),
                                dbc.Col(
                                    [
                                        dcc.Graph(
                                            id="exposure",
                                            figure={
                                                'data': [go.Pie(labels=["buildings", "roads", "agriculture"], values=["20", "35", "72"])], #placeholder pie chart ## needs to read in actual data
                                                'layout': go.Layout(title='Exposure Summary')
                                            },
                                            style={"height": "30vh"}
                                        ),
                                        html.Div(
                                            dcc.Graph(
                                                id="loss-and-damage",
                                                figure={
                                                'data': [go.Pie(labels=["buildings: $30k", "roads: $800k", "agriculture: $1m"], values=["30000", "800000", "1000000"])], #placeholder pie chart ## needs to read in actual data
                                                'layout': go.Layout(title='Loss and Damage Summary $USD')
                                            },
                                                style={"height": "30vh"}
                                            ),
                                            style={"marginTop": "10px"}  # Space between the two graphs
                                        ),
                                    ],
                                    width=4  # Width for the graph column
                                ),
                                # Column for Text Boxes
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.H4("National Level Exposure Summary:", style={"color": "black"}),
                                                html.P("Summary content goes here...", style={"color": "black", "height": "19vh"})  # Add your summary content
                                            ],
                                            style={"padding": "10px", "backgroundColor": "#ffffff", "marginBottom": "10px"}
                                        ),
                                        html.Div(
                                            [
                                                html.H4("National Level Loss and Damage Summary:", style={"color": "black"}),
                                                html.P("Summary content goes here...", style={"color": "black", "height": "16vh"})  # Add your summary content
                                            ],
                                            style={"padding": "10px", "backgroundColor": "#ffffff"}
                                        ),
                                    ],
                                    width=2  # Width for the text boxes column
                                ),
                            ],
                            style={"marginBottom": "10px"}
                        ),
                    ],
                    width=10,  # Width for the map and graph column
                ),
            ],
            style={"padding": "10px"}  # Add padding around the row
        ),
    ],
    style={"backgroundColor": "#CCCCFF", "color": "white", "padding": "20px"}  # Periwinkle background and white text color for the entire page
)
