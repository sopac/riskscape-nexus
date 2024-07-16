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

dash.register_page(__name__)


project_name = "tuvalu"

############################### LOAD DATA AND PREPARE DATA ###############################

#load regional summary
gdf_regional_summary = gpd.read_file(
    "data/" + project_name + "/" + "full-probabilistic-slr-regional-summary.geojson"
)
# rename regional summary columns for display
gdf_regional_summary.rename(
    columns={"Change.Average_Annual_Population_Exposed": "Change.Population_Exposed"},
    inplace=True,
)

# #regional impact
# gdf_regional_impact = gpd.read_file(
#     "data/"
#     + project_name
#     + "/"
#     + "full-probabilistic-slr-regional-impact-ari100.geojson"
# )

#load average loss
df_average_loss = pd.read_csv(
    "data/" + project_name + "/" + "full-probabilistic-slr-average-loss.csv"
)
#filter average loss for ssp245
df_average_loss_245 = df_average_loss[df_average_loss["Scenario"] == 'ssp245 (medium confidence)']

#load regional average loss
df_regional_average_loss = pd.read_csv(
    "data/" + project_name + "/" + "full-probabilistic-slr-regional-average-loss.csv"
)
#filter regional average loss for ssp245
df_regional_average_loss_245 = df_regional_average_loss[df_regional_average_loss["Scenario"] == 'ssp245 (medium confidence)']

# #national loss curve
# gdf_national_loss_curve = gpd.read_file(
#    "data/" + project_name + "/" + "coastal-slr-risk-national-loss-curve.geojson"
# )



############################### DROPDOWN SELECTION CONFIGURATION ###############################

# create region list for region selection dropdown
regions = gdf_regional_summary["Region"].tolist()
regions.sort()
regions = ['All regions'] + regions



############################### MAP COMPONENT ###############################

# mapinfo
colorscale = ["red", "yellow", "green", "blue", "purple"]  # rainbow



############################### MAP FEATURE INFO BOX ###############################
def get_info(feature=None):
    header = [html.B("Regional Summary")]
    if not feature:
        return header + [html.P("N/A")]
    id = feature["id"]
    print(id)
    # print(feature)
    # print("\r\n")
    # r = gdf_regional_summary.iloc[[int(id)]]["Region"].values[0]

    return header + [
        html.P(gdf_regional_summary.iloc[[int(id)]]["Region"].values[0]),
        html.Div(
            [
                html.Table(
                    [
                        html.Tr(
                            [
                                html.Td("Change.Total_AAL : "),
                                html.Td(
                                    str(
                                        round(
                                            gdf_regional_summary.iloc[[int(id)]][
                                                "Change.Total_AAL"
                                            ].values[0],
                                            2,
                                        )
                                    )
                                ),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td("Change.Building_AAL : "),
                                html.Td(
                                    str(
                                        round(
                                            gdf_regional_summary.iloc[[int(id)]][
                                                "Change.Building_AAL"
                                            ].values[0],
                                            2,
                                        )
                                    )
                                ),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td("Change.Crops_AAL : "),
                                html.Td(
                                    str(
                                        round(
                                            gdf_regional_summary.iloc[[int(id)]][
                                                "Change.Crops_AAL"
                                            ].values[0],
                                            2,
                                        )
                                    )
                                ),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td("Change.Road_AAL : "),
                                html.Td(
                                    str(
                                        round(
                                            gdf_regional_summary.iloc[[int(id)]][
                                                "Change.Road_AAL"
                                            ].values[0],
                                            2,
                                        )
                                    )
                                ),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td("Change.Infrastructure_AAL : "),
                                html.Td(
                                    str(
                                        round(
                                            gdf_regional_summary.iloc[[int(id)]][
                                                "Change.Infrastructure_AAL"
                                            ].values[0],
                                            2,
                                        )
                                    )
                                ),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td("Change.Population_Exposed : "),
                                html.Td(
                                    str(
                                        round(
                                            gdf_regional_summary.iloc[[int(id)]][
                                                "Change.Population_Exposed"
                                            ].values[0],
                                            2,
                                        )
                                    )
                                ),
                            ]
                        ),
                    ],
                    style={"border": "1px solid black"},
                ),
            ],
            style={"textAlign": "left"},
        ),
    ]


info = html.Div(
    children=get_info(),
    id="info",
    className="info",
    style={
        "position": "absolute",
        "top": "80px",
        "left": "10px",
        "zIndex": "1000",
        "background": "white",
    },
)




############################### DASHBOARD LAYOUT ###############################

layout = html.Div(
    [
        dbc.Row(
            dbc.Col(html.H3("Sea Level Rise (SLR)", style={"textAlign": "center"}))
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Country : ", style={"textAlign": "right"}),
                    ],
                    width=1,  # Adjust width as needed
                    style={"textAlign": "center"}  # Align label to the right
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            options=[
                                {"label": "Samoa", "value": "Samoa"},
                                {"label": "Tuvalu", "value": "Tuvalu"},
                                {"label": "Vanuatu", "value": "Vanuatu"},
                            ],
                            value="Tuvalu",
                            id="country-select",
                            style={"width": "100%"}  # Adjust width as needed
                        ),
                    ],
                    width=3,  # Adjust width as needed
                    align="center"  # Center align the content
                ),
                dbc.Col(
                    [
                        html.Label("Region : ", style={"textAlign": "right"}),
                    ],
                    width=3,  # Adjust width as needed
                    style={"textAlign": "right"}  # Align label to the right
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            options=[{"label": region, "value": region} for region in regions],
                            value="All regions",
                            id="region-select",
                            style={"width": "100%"}  # Adjust width as needed
                        ),
                    ],
                    width=3,  # Adjust width as needed
                    align="center"  # Center align the content
                ),
            ],
            justify="center",  # Center align the row content
            style={"marginBottom": "10px"}  # Add margin to the row
        ),
        dbc.Row(html.Br()),
        dbc.Row(
            [
                dbc.Col(html.B("Impact By Region")),
                dbc.Col(html.B("AAL Change Between 2020 And 2150 By Region (ssp245)")),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dl.Map(
                        [
                            # dl.TileLayer(
                            #    url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                            # ),
                            dl.TileLayer(),
                            dl.GeoJSON(
                                data=json.loads(
                                   gdf_regional_summary["geometry"].to_json()
                                ),
                                id="map-region-impact",
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
                            info,
                        ],
                        zoom=6,
                        style={"height": "40vh"},
                        center=(
                            gdf_regional_summary.dissolve().centroid.y.values[0].item(),
                            gdf_regional_summary.dissolve().centroid.x.values[0].item(),
                        ),
                    )
                ),
                dbc.Col(
                    dcc.Graph(
                        id="graph-regional-summary",
                        style={"height": "40vh"},
                    )
                ),
            ]
        ),
        dbc.Row(html.Br()),
        dbc.Row(
            [
                dbc.Col(html.B("AAL by Province (ssp245) averaged over 130 years")),
                dbc.Col(html.B("National Loss Curve (ssp245)")),
            ]
        ),
        dbc.Row(
            [
                # dbc.Col(html.H3("sdsdd")),
                dbc.Col(
                    dcc.Graph(
                        # id="graph-regional-loss-curve",
                        style={"height": "40vh"},
                        figure=px.histogram(
                            df_regional_average_loss_245,
                            x="Region",
                            y=[
                                #"Total_AAL",
                                "Building_AAL",
                                "Crops_AAL",
                                "Road_AAL",
                                "Infrastructure_AAL",
                                # "Average_Annual_Population_Exposed",
                            ],
                            histfunc="avg",
                        ).update_layout(xaxis_title="Province", yaxis_title="Avg. Loss USD"),
                    )
                ),
                dbc.Col(
                    dcc.Graph(
                        # id="graph-national-loss-curve",
                        figure=px.line(
                            df_average_loss_245,
                            x="Year",
                            y=[
                                "Total_AAL",
                                "Building_AAL",
                                "Crops_AAL",
                                "Road_AAL",
                                "Infrastructure_AAL"
                                # "Average_Annual_Population_Exposed",
                            ],
                            markers=True,
                        ).update_layout(xaxis_title="Year", yaxis_title="Loss USD"),
                        style={"height": "40vh"},
                    )
                ),
            ]
        ),
    ],
    style={"textAlign": "center"},
)



############################### CALLBACKS ###############################

#map: zoom map to selected region 
@callback(Output("map-region-impact", "data"), Input("region-select", "value"))
def update_map(value):
    if value == 'All regions':
        gdf_regional_summary_filtered = gdf_regional_summary
    else:
        gdf_regional_summary_filtered = gdf_regional_summary[
            gdf_regional_summary["Region"] == value
        ]
    data = json.loads(
        gdf_regional_summary_filtered["geometry"].to_json(),
        object_pairs_hook=OrderedDict,
    )

    return data

#map: retrieve feature info for info box
@callback(Output("info", "children"), Input("map-region-impact", "hoverData"))
def info_hover(feature):
    return get_info(feature)

#regional summary graph: display data from selected region
@callback(Output("graph-regional-summary", "figure"), Input("region-select", "value"))
def update_graph_regional_summary(value):
    # print(value)
    if value == None: #this is a bit of a hack - value is never None, but this way the empty grpah looks nicest for now
        gdf_regional_summary_filtered = gdf_regional_summary
    else:
        gdf_regional_summary_filtered = gdf_regional_summary[
            gdf_regional_summary["Region"] == value
        ]
    figure = px.bar(
        gdf_regional_summary_filtered,
        x="Region",
        y=[
            "Change.Total_AAL",
            "Change.Building_AAL",
            "Change.Crops_AAL",
            "Change.Road_AAL",
            "Change.Infrastructure_AAL",
            # "Change.Population_Exposed",
        ],
        barmode="group",
    ).update_layout(xaxis_title="Region", yaxis_title="Loss USD")
    return figure
