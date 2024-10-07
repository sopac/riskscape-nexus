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
from dash_bootstrap_templates import load_figure_template

dash.register_page(__name__, external_stylesheets=[dbc.themes.SLATE])

load_figure_template('slate') # template for charts
project_name = "tonga"

color_map = ['#DBBF21', '#BD3539', '#57C560', '#F19502', '#81D6F6', '#5D6167', '#D169C1']


############################### LOAD DATA AND PREPARE DATA ###############################

#  datasets  #
#load regional summary
gdf_regional_summary = gpd.read_file(
    "data/" + project_name + "/" + "full-probabilistic-slr-regional-summary.geojson"
)
# rename regional summary columns for display
gdf_regional_summary.rename(
    columns={"Change.Average_Annual_Population_Exposed": "Change.Population_Exposed"},
    inplace=True,
)

#  CSV's  #
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



############################### LAYOUT COMPONENTS ###############################

### DROPDOWN - region
# create region list for region selection dropdown
regions = gdf_regional_summary["Region"].tolist()
regions.sort()
regions = ['All regions'] + regions
# define dropdown object
dropdown_region = dcc.Dropdown(
    options=[{"label": region, "value": region} for region in regions],
    value="All regions",
    id="region-select"
)

### CHART - avg aal by province
chart_aal_province = dcc.Graph(
    # id="graph-regional-loss-curve",
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
    style={"height": "35vh"},
)

chart_aal_national = dcc.Graph(
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
    style={"height": "35vh"},
)

### MAP FEATURE INFO BOX
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

### MAP
map = dl.Map([
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
            ),
        ),
        info,
    ],
    zoom=6,
    style={"height": "35vh"},
    center=(
        gdf_regional_summary.dissolve().centroid.y.values[0].item(),
        gdf_regional_summary.dissolve().centroid.x.values[0].item(),
    ),
)


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

layout = html.Div(children=[
        dbc.Row([
                dbc.Col([
                    html.B("Region : ")
                ], width=3),
                dbc.Col([
                    dropdown_region
                ],  width=6)
            ]),
        dbc.Row(html.Br()),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.B("Impact By Region"),
                        map
                    ])
                ]),
                html.Br(),
                dbc.Card([
                    dbc.CardBody([
                        html.B("AAL by Province (ssp245) averaged over 130 years"),
                        chart_aal_province
                    ])
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.B("AAL Change Between 2020 And 2150 By Region (ssp245)"),
                        dcc.Graph(
                            id="graph-regional-summary",
                            style={"height": "35vh"},
                        )
                    ])
                ]),
                html.Br(),
                dbc.Card([
                    dbc.CardBody([
                        html.B("National Loss Curve (ssp245)"),
                        chart_aal_national
                    ])
                ])
            ])
        ])
    ],
    style={"textAlign": "center", "padding": "10px"}
)



############################### CALLBACKS ###############################

### MAP: zoom map to selected region 
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


### MAP: retrieve feature info for info box
@callback(Output("info", "children"), Input("map-region-impact", "hoverData"))
def info_hover(feature):
    return get_info(feature)


### CHART: regional summary graph
@callback(
        Output("graph-regional-summary", "figure"), 
        Input("region-select", "value")
        )
def update_graph_regional_summary(value):
    if value == None: #this is a bit of a hack - value is never None, but this way the empty grpah looks nicest for now
        gdf_regional_summary_filtered = gdf_regional_summary
    else:
        gdf_regional_summary_filtered = gdf_regional_summary[
            gdf_regional_summary["Region"] == value
        ]
    fig = px.bar(
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
    
    return fig
