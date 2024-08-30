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
import rasterio
from rasterio.plot import show
from rasterio import features
from shapely.geometry import shape
import matplotlib as plt
from PIL import Image
import base64


dash.register_page(__name__)

project_name = "pdna"

############################### LOAD DATA AND PREPARE RISKSCAPE DATA ###############################

#  GEOJSONS  #
#load cyclone track
gdf_cyclone_track = gpd.read_file("data/" + project_name + "/" + "cyclone-track.geojson")

#load damaged buildings
gdf_damaged_buildings = gpd.read_file("data/" + project_name + "/" + "damaged-buildings.geojson")

#load damaged roads
gdf_damaged_roads = gpd.read_file("data/" + project_name + "/" + "damaged-roads.geojson")

#load exposure by cluster
gdf_exposure_by_cluster = gpd.read_file( "data/" + project_name + "/" + "exposure-by-cluster.geojson")

#load regional impacts
gdf_regional_impacts = gpd.read_file("data/" + project_name + "/" + "regional-impacts.geojson")


#  CSV's  #
#load impact by asset type
df_impact_by_asset_type = pd.read_csv("data/" + project_name + "/" + "impact-by-asset-type.csv")

#load national summary
df_national_summary = pd.read_csv("data/" + project_name + "/" + "national-summary.csv")

#load regional summary
df_regional_summary = pd.read_csv("data/" + project_name + "/" + "regional-summary.csv")


############################### DASH CALLBACK FOR MAP ###############################

# Dictionary of country coordinates
country_coordinates = {
    "Vanuatu": {"center": (-18, -190)},
    "Samoa": {"center": (-14, -170)},
    "Cook Islands": {"center": (-21, -159)},
    "Tonga": {"center": (-20, -178)},
}

@callback(
    Output("pdna-map", "center"),
    Output("pdna-map", "zoom"),
    Input("country-select", "value")
)
def update_map_extent(selected_country):
    # Set the zoom level to a constant value of 5
    zoom = 5
    
    if selected_country in country_coordinates:
        # Get the center for the selected country
        center = country_coordinates[selected_country]["center"]
    else:
        # Default to Pacific region if no country is selected or the country is not in the dictionary
        center = (-16, -170)
    
    return center, zoom


############################### DASH CALLBACK FOR MAP LAYERS ###############################

# Base URL for the GeoServer WMS
GEOSERVER_URL = "https://nexus.pacificdata.org/geoserver/geonode/wms"

@callback(
    Output("pdna-map", "children"),
    Input("hazard-select", "value")
)
def update_map_layer(selected_hazards):
    layers = [dl.TileLayer()]  # Base map layer

    for hazard in selected_hazards:
        if hazard == "Cyclone Track":
            layers.append(
                dl.GeoJSON(
                    data=json.loads(gdf_cyclone_track.to_json()), 
                    id="cyclone-track",
                    zoomToBounds=True,
                    zoomToBoundsOnClick=True,
                    style=dict(
                        weight=2,
                        opacity=1,
                        color="red",
                        fillOpacity=0.5,
                    ),
                )
            )

        elif hazard == "Coastal Inundation":
            layers.append(
                dl.WMSTileLayer(
                    url=GEOSERVER_URL,
                    layers="geonode:tc_lola_coastalinundation",
                    format="image/png",
                    transparent=True,
                    id="inundation-layer"
                )
            )

        # elif hazard == "Storm Surge":
        #     layers.append(
        #         dl.WMSTileLayer(
        #             url=GEOSERVER_URL,
        #             layers="geonode:storm_surge",
        #             format="image/png",
        #             transparent=True,
        #             id="storm_surge-layer"
        #         )
        #     )

        elif hazard == "Wave Height":
            layers.append(
                dl.WMSTileLayer(
                    url=GEOSERVER_URL,
                    layers="	geonode:tc_lola_hs_max",
                    format="image/png",
                    transparent=True,
                    id="wave_height-layer"
                )
            )
    
    return layers  # Always return the base map layer + any additional layers

############################### DASH CALLBACK FOR HOVERING ###############################

# # Display detailed information on hover or click on the map 

# @callback(
#     Output("exposure-summary-text", "children"),
#     Output("loss-damage-summary-text", "children"),
#     Input("pdna-map", "clickData")
# )
# def display_map_info(click_data):
#     if click_data is None:
#         return "Click on an area to see details.", "Click on an area to see details."
    
#     # Extract data from click_data
#     location_info = click_data['points'][0]
#     location_name = location_info.get('text', 'Unknown location')
    
#     # Look up details based on location_name or coordinates
#     exposure_summary = f"Exposure summary for {location_name}..."
#     loss_damage_summary = f"Loss and damage summary for {location_name}..."
    
#     return exposure_summary, loss_damage_summary


############################### DASH CALLBACK FOR GRAPHS ###############################

# # Update graphs based on selected cluster and aggregation level

# @callback(
#     Output("exposure", "figure"),
#     Output("loss-and-damage", "figure"),
#     Input("cluster-select", "value"),
#     Input("aggregation-select", "value")
# )
# def update_graphs(selected_cluster, selected_aggregation):
#     # Filter data based on selections
#     filtered_df = df_impact_by_asset_type[(df_impact_by_asset_type['Cluster'] == selected_cluster) & 
#                                           (df_impact_by_asset_type['Aggregation'] == selected_aggregation)]
    
#     exposure_data = go.Pie(
#         labels=filtered_df['Asset_Type'].tolist(),
#         values=filtered_df['Exposure'].tolist()
#     )
    
#     loss_data = go.Pie(
#         labels=filtered_df['Asset_Type'].tolist(),
#         values=filtered_df['Loss_and_Damage'].tolist()
#     )

#     return (
#         {"data": [exposure_data], "layout": go.Layout(title="Exposure Summary")},
#         {"data": [loss_data], "layout": go.Layout(title="Loss and Damage Summary $USD")}
#     )

############################### DASH CALLBACK FOR SUMMARIES ###############################

# Non-interactive National Level Summary Boxes

# Exposure Summary Box
@callback(
    Output("national-summary-text", "children"),
    Input("interval-component", "n_intervals")  # Trigger callback on every interval tick
)
def update_national_summary(n_intervals):
    # Titles to look for
    titles = [
        "Buildings_Exposed_To_Any_Hazard", 
        "Population_Exposed_To_Any_Hazard", 
        "Exposed_Infrastructure", 
        "Exposed_Evacuation_Centres", 
        "Exposed_Health_Facilties", 
        "Exposed_Schools"
    ]

    # Find the corresponding values
    values = [df_national_summary[title].values[0] for title in titles]

    # Create a list of html.P elements, each representing a line of text
    summary_text = [
        html.P(f"{title.replace('_', ' ')}: {value}", style={"font-family": "Times New Roman", "font-size": "14px"}) 
        for title, value in zip(titles, values)
    ]
    
    return summary_text  # Return the list of html.P elements


# Damage Summary Box
@callback(
    Output("damage-summary-text", "children"),
    Input("interval-component", "n_intervals")  # Use the interval to trigger the update
)
def update_loss_damage_summary(n_intervals):
    # Start from the second row (index 1)
    titles = df_impact_by_asset_type.iloc[1:, 0].tolist()  # First column contains the titles
    values = df_impact_by_asset_type.iloc[1:, 1].tolist()  # Second column contains the values

    # Join each title and value with a newline 
    summary_text = "\n".join([f"{title}: {value}" for title, value in zip(titles, values)])
    
    # Return the formatted summary as a string 
    return html.Pre(f"{summary_text}", style={"font-family": "Times New Roman", "font-size": "14px"})


############################### DASHBOARD LAYOUT ###############################
layout = html.Div(
    [
        dbc.Row(
            dbc.Col(
                html.H3("Post Disaster Impact Assessment (PDIA)", style={"textAlign": "center", "color": "black"})
            ),
            style={"backgroundColor": "#eaeded", "padding": "10px"}  # background for the header row
        ),
        dbc.Row(
            [
                # Column for Dropdowns
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.P("Please select a country for analysis:", style={"color": "black"}),
                                html.Label("Country:", style={"color": "black"}),
                                dcc.Dropdown(
                                    options=[
                                        {"label": "Tonga", "value": "Tonga"},
                                        {"label": "Samoa", "value": "Samoa"},
                                        {"label": "Cook Islands", "value": "Cook Islands"},
                                        {"label": "Vanuatu", "value": "Vanuatu"},
                                    ],
                                    value="",
                                    id="country-select",
                                    style={"width": "100%", "backgroundColor": "#ffffff", "color": "black"}  # Dropdown background color
                                ),
                            ],
                            style={"marginBottom": "10px"}
                        ),
                        html.Div(
                            [
                                html.P("Please select the hazard you want visualized on the map:", style={"color": "black"}),
                                html.Label("Hazard:", style={"color": "black"}),
                                dcc.Dropdown(
                                    options=[
                                        {"label": "Wave Height", "value": "Wave Height"},
                                        {"label": "Coastal Inundation", "value": "Coastal Inundation"},
                                        {"label": "Cyclone Track", "value": "Cyclone Track"},
                                        {"label": "Storm Surge", "value": "Storm Surge"},
                                    ],
                                    value="", # No default seclection
                                    id="hazard-select",
                                    multi=True, # Enable multiple selections
                                    style={"width": "100%", "backgroundColor": "#ffffff", "color": "black"}  # Dropdown background color
                                ),
                            ],
                            style={"marginBottom": "10px"}
                        ),
                        html.Div(
                            [
                                html.P("Please select the cross sectoral cluster you want to analyse:", style={"color": "black"}),
                                html.Label("Cluster:", style={"color": "black"}),
                                dcc.Dropdown(
                                    options=[
                                        {"label": "Agriculture", "value": "Agriculture"},
                                        {"label": "Social", "value": "Social"},
                                        {"label": "Health", "value": "Health"},
                                    ],
                                    value="",
                                    id="cluster-select",
                                    style={"width": "100%", "backgroundColor": "#ffffff", "color": "black"}  # Dropdown background color
                                ),
                            ],
                            style={"marginBottom": "10px"}
                        ),
                        html.Div(
                            [
                                html.P("Please select the aggregation level you would the anaylsis performed at:", style={"color": "black"}),
                                html.Label("Aggregation:", style={"color": "black"}),
                                dcc.Dropdown(
                                    options=[
                                        {"label": "National", "value": "National"},
                                        {"label": "Regional", "value": "Regional"}
                                    ],
                                    value="",
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
                                        ],
                                        style={"height": "60vh"},
                                        zoom=5,
                                        center=(-16, -170),  # Central coordinates for the Pacific region
                                        id="pdna-map",
                                        viewport={"center": [-16, -170], "zoom": 5},  # Track the map's viewport
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
                                                'layout': go.Layout(title='Damage Summary $USD')
                                            },
                                                style={"height": "30vh"}
                                            ),
                                            style={"marginTop": "10px"}  # Space between the two graphs
                                        ),
                                    ],
                                    width=3  # Width for the graph column
                                ),
                                # Column for Text Boxes
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.H4("National Level Exposure Summary:", style={"color": "black"}),
                                                html.Div(id="national-summary-text", style={"color": "black", "height": "22vh"}),
                                                dcc.Interval(
                                                    id="interval-component",
                                                    interval=1*5000000,  # Adjust the interval as needed
                                                    n_intervals=0
                                                ),
                                            ],
                                            style={"padding": "10px", "backgroundColor": "#ffffff", "marginBottom": "10px"}
                                        ),
                                        html.Div(
                                            [
                                                html.H4("National Level Damage Summary ($USD):", style={"color": "black"}),
                                                html.Div(id="damage-summary-text", style={"color": "black", "height": "24vh"}),
                                                dcc.Interval(
                                                    id="interval-component",
                                                    interval=1*5000000,  # Adjust the interval as needed
                                                    n_intervals=0
                                                ),
                                            ],
                                            style={"padding": "10px", "backgroundColor": "#ffffff"}
                                        ),
                                    ],
                                    width=3  # Width for the text boxes column
                                ),
                            ],
                            style={"marginBottom": "10px"}
                        ),
                    ],
                    width=10,  # Width for the map, graph and textbox column
                ),
            ],
            style={"padding": "10px"}  # Add padding around the row
        ),
    ],
    style={"backgroundColor": "#eaeded", "color": "white", "padding": "20px"}  # gray background and for the entire page
)


