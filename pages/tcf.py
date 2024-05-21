import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import geopandas as gpd
import pandas as pd
import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_dangerously_set_inner_html
import json

dash.register_page(__name__)

# load data
project_name = "vanuatu"
# maps
gdf_regional_exposure = gpd.read_file(
    "data/" + project_name + "/" + "jtwc-forecast-regional-exposure.geojson"
)
gdf_cyclone_track = gpd.read_file(
    "data/" + project_name + "/" + "cyclone-pdna-cyclone-track.geojson"
)
# data
df_regional_summary = pd.read_csv(
    "data/" + project_name + "/" + "jtwc-forecast-regional-summary.csv"
)


def get_info(feature=None):
    header = [html.B("Regional Exposure")]
    if not feature:
        return header + [html.P("N/A")]
    id = feature["id"]
    # print(id)

    return header + [
        html.P(gdf_regional_exposure.iloc[[int(id)]]["map_region.eaname"].values[0]),
        html.Div(
            [
                dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
                    f"""
        
        <table style='border: 1px'>
          <tr>
           <td>Buildings Affected : </td/>
           <td>{gdf_regional_exposure.iloc[[int(id)]]["Buildings"].values[0]}</td/>
          </tr>
          <tr>
           <td>Population Affected : </td/>
           <td>{gdf_regional_exposure.iloc[[int(id)]]["Population"].values[0]}</td/>
          </tr>
          <tr>
           <td>Max KM/ph : </td/>
           <td>{gdf_regional_exposure.iloc[[int(id)]]["max_kmph"].values[0]}</td/>
          </tr>
          <tr>
           <td>Min KM/ph : </td/>
           <td>{gdf_regional_exposure.iloc[[int(id)]]["min_kmph"].values[0]}</td/>
          </tr>
          <tr>
           <td>Track KM/ph : </td/>
           <td>{gdf_regional_exposure.iloc[[int(id)]]["track_kmph"].values[0]}</td/>
          </tr>
        </table>

    """
                ),
            ],
            style={"textAlign": "left"},
        ),
    ]
    return header


info = html.Div(
    children=get_info(),
    id="info-tc",
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
            dbc.Col(
                html.H3(
                    "Rapid Exposure Forecase for Tropical Cyclone Scenarios",
                    style={"textAlign": "center"},
                )
            )
        ),
        dbc.Row(html.Br()),
        dbc.Row(
            [
                dbc.Col(html.Label("Tropical Cyclone : "), width=3),
                dbc.Col(
                    dcc.Dropdown(
                        ["TC Lola (Vanuatu)", "Cook-Islands", "Tonga", "Samoa"],
                        "TC Lola (Vanuatu)",
                        id="country-select",
                    ),
                    width=6,
                ),
            ]
        ),
        dbc.Row(html.Br()),
        dbc.Row(
            [
                dbc.Col(html.B("Regional Exposure and Track Path")),
                dbc.Col(html.B("")),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dl.Map(
                        [
                            dl.TileLayer(),
                            dl.GeoJSON(
                                id="map-regional-exposure",
                                data=json.loads(
                                    gdf_regional_exposure["geometry"].to_json()
                                ),
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
                            dl.GeoJSON(
                                data=json.loads(
                                    gdf_cyclone_track["geometry"].to_json()
                                ),
                                zoomToBounds=True,
                                zoomToBoundsOnClick=True,
                                style=dict(
                                    weight=2,
                                    opacity=1,
                                    color="blue",
                                    fillOpacity=0.5,
                                ),
                            ),
                        ],
                        zoom=6,
                        style={"height": "60vh"},
                        center=(
                            gdf_regional_exposure.dissolve()
                            .centroid.y.values[0]
                            .item(),
                            gdf_regional_exposure.dissolve()
                            .centroid.x.values[0]
                            .item(),
                        ),
                    )
                ),
                dbc.Col(
                    dbc.Row(
                        [
                            # bar chart - buildings per windspeed
                            html.B("Buildings Exposed by Windspeed"),
                            dcc.Graph(
                                figure=px.histogram(
                                    gdf_regional_exposure,
                                    x="max_kmph",
                                    y="Buildings",
                                    histfunc="avg",
                                    color='max_kmph',
                                ).update_layout(
                                    xaxis_title="Maximum Windspeed (KM/ph)",
                                    yaxis_title="No. Of Buildings Exposed",
                                ),
                                style={"height": "30vh"},
                            ),
                            # bar chart - population per windspeed
                            html.B("Population Exposed by Windspeed"),
                            dcc.Graph(
                                figure=px.histogram(
                                    gdf_regional_exposure,
                                    x="max_kmph",
                                    y="Population",
                                    histfunc="avg",
                                    color='max_kmph',
                                ).update_layout(
                                    xaxis_title="Maximum Windspeed (KM/ph)",
                                    yaxis_title="Population Exposed.",
                                ),
                                style={"height": "30vh"},
                            ),
                            # html.B("title 4"),
                            # bar chart - total value per windspeed (??)
                        ]
                    )
                ),
            ]
        ),
    ],
    style={"textAlign": "center"},
)


@callback(Output("info-tc", "children"), Input("map-regional-exposure", "hoverData"))
def info_hover(feature):
    return get_info(feature)
