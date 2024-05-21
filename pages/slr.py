import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import geopandas as gpd
import pandas as pd
import dash_leaflet as dl
import dash_leaflet.express as dlx
import json

dash.register_page(__name__)

project_name = "vanuatu"

# load data single
gdf_regional_summary = gpd.read_file(
    "data/" + project_name + "/" + "full-probabilistic-slr-regional-summary.geojson"
)

gdf_regional_impact = gpd.read_file(
    "data/"
    + project_name
    + "/"
    + "full-probabilistic-slr-regional-impact-ari100.geojson"
)

df_average_loss = pd.read_csv(
    "data/" + project_name + "/" + "full-probabilistic-slr-average-loss.csv"
)

df_regional_average_loss = pd.read_csv(
    "data/" + project_name + "/" + "full-probabilistic-slr-regional-average-loss.csv"
)


# gdf_national_loss_curve = gpd.read_file(
#    "data/" + project_name + "/" + "coastal-slr-risk-national-loss-curve.geojson"
# )

# gdf_regional_summary = gdf_regional_summary.to_crs('epsg:3587')

# lists
regions = gdf_regional_summary["Region"].tolist()
regions.sort()

# rename
gdf_regional_summary.rename(
    columns={"Change.Average_Annual_Population_Exposed": "Change.Population_Exposed"},
    inplace=True,
)


# mapinfo
colorscale = ["red", "yellow", "green", "blue", "purple"]  # rainbow


def get_info(feature=None):
    header = [html.B("Regional Summary")]
    if not feature:
        return header + [html.P("N/A")]
    id = feature["id"]
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

layout = html.Div(
    [
        dbc.Row(
            dbc.Col(html.H3("Sea Level Rise (SLR)", style={"textAlign": "center"}))
        ),
        dbc.Row(
            [
                dbc.Col(html.Label("Country (Project) : "), width=3),
                dbc.Col(
                    dcc.Dropdown(
                        ["Cook-Islands", "Tonga", "Samoa", "Vanuatu"],
                        "Vanuatu",
                        id="country-select",
                    ),
                    width=6,
                ),
            ]
        ),
        dbc.Row(html.Br()),
        dbc.Row(
            [
                dbc.Col(html.Label("Region (Island) : "), width=3),
                dbc.Col(
                    dcc.Dropdown(
                        regions,
                        "",
                        id="region-select",
                    ),
                    width=6,
                ),
                html.Br(),
            ]
        ),
        dbc.Row(html.Br()),
        dbc.Row(
            [
                dbc.Col(html.B("Impact By Island")),
                dbc.Col(html.B("AAL Change By Island")),
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
                                # data=json.loads(
                                #    gdf_regional_impact["geometry"].to_json()
                                # ),
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
                            gdf_regional_impact.dissolve().centroid.y.values[0].item(),
                            gdf_regional_impact.dissolve().centroid.x.values[0].item(),
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
                dbc.Col(html.B("Average Annual Loss by Province (ssp245)")),
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
                            df_regional_average_loss,
                            x="Region",
                            y=[
                                "Total_AAL",
                                "Building_AAL",
                                "Crops_AAL",
                                "Road_AAL",
                                "Infrastructure_AAL",
                                "Average_Annual_Population_Exposed",
                            ],
                            histfunc="avg",
                        ),
                    )
                ),
                dbc.Col(
                    dcc.Graph(
                        # id="graph-national-loss-curve",
                        figure=px.line(
                            df_average_loss,
                            x="Year",
                            y=[
                                "Total_AAL",
                                "Building_AAL",
                                "Crops_AAL",
                                "Road_AAL",
                                "Infrastructure_AAL",
                                "Average_Annual_Population_Exposed",
                            ],
                            markers=True,
                        ),
                        style={"height": "40vh"},
                    )
                ),
            ]
        ),
    ],
    style={"textAlign": "center"},
)

# callbacks


@callback(Output("info", "children"), Input("map-region-impact", "hoverData"))
def info_hover(feature):
    return get_info(feature)


@callback(Output("map-region-impact", "data"), Input("region-select", "value"))
def update_graph(value):
    if value == None:
        gdf_regional_impact_filtered = gdf_regional_impact
    else:
        gdf_regional_impact_filtered = gdf_regional_impact[
            gdf_regional_impact["Region"] == value
        ]
    data = json.loads(gdf_regional_impact_filtered["geometry"].to_json())
    return data


@callback(Output("graph-regional-summary", "figure"), Input("region-select", "value"))
def update_graph_regional_summary(value):
    # print(value)
    if value == None:
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
            "Change.Population_Exposed",
        ],
        barmode="group",
        # text_auto=False,
        # labels=["Total", "Building"],
    )
    return figure
