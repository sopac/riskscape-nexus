import dash
from dash import Dash, html, dcc, callback, Output, Input, State
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



dash.register_page(__name__)

project_name = "cooks_pdia"

############################### LOAD DATA AND PREPARE RISKSCAPE DATA ###############################

#  datasets  #
#load damaged buildings
gdf_damaged_buildings = gpd.read_file("data/" + project_name + "/" + "damaged-buildings.gpkg")

#load damaged roads
gdf_damaged_roads = gpd.read_file("data/" + project_name + "/" + "damaged-roads.gpkg")

#load exposure by cluster
gdf_exposure_by_cluster = gpd.read_file( "data/" + project_name + "/" + "exposure-by-cluster.geojson")

#load regional impacts by sector
gdf_regional_impacts_by_sector = gpd.read_file("data/" + project_name + "/" + "regional-impacts-by-sector.geojson")

#load regional impacts
gdf_regional_impacts = gpd.read_file("data/" + project_name + "/" + "regional-impacts.geojson")


#  CSV's  #
#load impact by asset type
df_impact_by_asset_type = pd.read_csv("data/" + project_name + "/" + "impact-by-asset-type.csv")

#load national impacts by sector
df_national_impact_by_sector = gpd.read_file("data/" + project_name + "/" + "national-impact-by-sector.csv")

#load national summary
df_national_summary = pd.read_csv("data/" + project_name + "/" + "national-summary.csv")

#load regional summary
df_regional_summary = pd.read_csv("data/" + project_name + "/" + "regional-summary.csv")

#load regional summary by sector
df_regional_summary_by_sector = gpd.read_file("data/" + project_name + "/" + "regional-summary-by-sector.csv")


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
                dl.WMSTileLayer(
                    url=GEOSERVER_URL,
                    layers="geonode:ref_tc_meena_cook_islands_cyclone_track", 	
                    format="image/png",
                    transparent=True,
                    id="cyclone-track-layer"
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

        elif hazard == "Wind":
            layers.append(
                dl.WMSTileLayer(
                    url=GEOSERVER_URL,
                    layers="geonode:ref_tc_meena_cook_islands_wind_swaths",
                    format="image/png",
                    transparent=True,
                    id="wind-swath-layer"
                )
            )

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

############################### DASH CALLBACK FOR GRAPHS ###############################

# Update graphs based on selected cluster and aggregation level

@callback(
    Output("exposure", "figure"),
    Input("cluster-select", "value"),
    Input("aggregation-select", "value")
)
def update_exposure_graph(selected_cluster, selected_aggregation):
    # Check if both selections are made
    if not selected_cluster or not selected_aggregation:
        return go.Figure(
            data=[],
            layout=go.Layout(
                title="Exposure Summary",
                xaxis_title="Sector",
                yaxis_title="Values",
                annotations=[{
                    "text": "Select Aggregation Level and Cluster to view the data.",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 10}
                }]
            )
        )
    
    # Handle National Aggregation
    if selected_aggregation.lower() == "national":
        df = df_national_impact_by_sector.copy()
        
        # Validate if the selected cluster exists in the dataframe
        if selected_cluster not in df.columns:
            return go.Figure(
                data=[],
                layout=go.Layout(
                    title="Exposure Summary",
                    xaxis_title="Sector",
                    yaxis_title="Values",
                    annotations=[{
                        "text": f"No data available for the selected cluster: {selected_cluster}.",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 12}
                    }]
                )
            )
        
        # Select rows 2 to 12 (index 1 to 11)
        data_subset = df.loc[0:10, ['Sector', selected_cluster]]
        
        # Handle empty or NaN values
        data_subset = data_subset.dropna()
        
        # Create Bar Chart
        fig = go.Figure(
            data=[
                go.Bar(
                    x=data_subset['Sector'],
                    y=data_subset[selected_cluster],
                    marker_color='indianred',
                )
            ],
            layout=go.Layout(
                title={
                    'text': f'National Level Exposure of {selected_cluster}',
                    'font': {
                        'size': 14  # Adjust the font size here
                    }
                },
                yaxis_title="Value",
                template="plotly_white"
            )
        )
        return fig
    
    else:
        # Placeholder for other aggregation levels like 'Regional'
        return go.Figure(
            data=[],
            layout=go.Layout(
                title="Exposure Summary",
                xaxis_title="Categories",
                yaxis_title="Values",
                annotations=[{
                    "text": f"Aggregation level '{selected_aggregation}' is not implemented yet.",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 12}
                }]
            )
        )

# Update damage summary graph based on selected hazard

@callback(
    Output("loss-and-damage", "figure"),
    [Input("hazard-select", "value"),
     Input("aggregation-select", "value")]
)
def update_damage_summary_graph(selected_hazards, selected_aggregation):
    # Check if aggregation level is National
    if selected_aggregation.lower() != "national":
        return go.Figure(
            data=[],
            layout=go.Layout(
                title="Damage Summary",
                annotations=[{
                    "text": f"Aggregation level '{selected_aggregation}' is not implemented for damage summary.",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 14}
                }]
            )
        )
    
    # Check if multiple hazards are selected
    if len(selected_hazards) > 1:
        return go.Figure(
            data=[],
            layout=go.Layout(
                title="Damage Summary",
                xaxis_title="Hazard",
                yaxis_title="Value",
                annotations=[{
                    "text": "Please select only one hazard.",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 14}
                }]
            )
        )
    
    # Handle the case where exactly one hazard is selected
    if len(selected_hazards) == 1:
        hazard = selected_hazards[0]
        
        # Determine the corresponding row based on the selected hazard
        row_title = ""
        if hazard == "Wind":
            row_title = "Total_Wind_Loss"
        elif hazard == "Cyclone Track":
            row_title = "Total_Loss"
        else:
            return go.Figure(
                data=[],
                layout=go.Layout(
                    title="Damage Summary",
                    xaxis_title="Hazard",
                    yaxis_title="Value",
                    annotations=[{
                        "text": "Invalid hazard selected.",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 14}
                    }]
                )
            )
        
        # Fetch the data for the selected hazard
        if row_title in df_national_impact_by_sector['Sector'].values:
            row_data = df_national_impact_by_sector[df_national_impact_by_sector['Sector'] == row_title].iloc[0, 1:]
            
            # Prepare the data for the pie chart
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=row_data.index,
                        values=row_data.values,
                    )
                ],
                layout=go.Layout(
                    title=f'Damage Summary for {hazard}',
                    template="plotly_white"
                )
            )
            return fig
        else:
            return go.Figure(
                data=[],
                layout=go.Layout(
                    title="Damage Summary",
                    xaxis_title="Hazard",
                    yaxis_title="Value",
                    annotations=[{
                        "text": "Data not available for the selected hazard.",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 14}
                    }]
                )
            )
    else:
        # Default case if no hazard is selected
        return go.Figure(
            data=[],
            layout=go.Layout(
                title="Damage Summary",
                xaxis_title="Hazard",
                yaxis_title="Value",
                annotations=[{
                    "text": "Select a hazard to view the data.",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 14}
                }]
            )
        )


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
                                        {"label": "Wind", "value": "Wind"},
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
                                        {"label": "Residential", "value": "Residential"},
                                        {"label": "Productive", "value": "Productive"},
                                        {"label": "Infrastructure", "value": "Infrastructure"},
                                        {"label": "Education", "value": "Education"},
                                        {"label": "Public", "value": "Public"},
                                        {"label": "Others", "value": "Others"},
                                        {"label": "Unknown", "value": "Unknown"},
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


