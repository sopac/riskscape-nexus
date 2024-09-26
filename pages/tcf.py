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
from dash import Dash, dash_table

dash.register_page(__name__)

# load data
project_name = "tc_harold_tonga"

############################### LOAD DATA AND PREPARE RISKSCAPE DATA ###############################

# tc meena data is for Cooks. 
# tc harold data is for Tonga
# tc lola data is for Vanuatu
# Below implemented some hard coded filtering to focus on specific country and tc. Eventually it should only choose the TC and show all countries for which there is data for it (?)


# data for the map
gdf_regional_exposure = gpd.read_file(
    # "data/" + "vanuatu" + "/" + "jtwc-forecast-regional-exposure.geojson"
    "data/rsmc-tcwc/" + project_name + "/" + "rapid-exposure-forecast-regional-impacts.geojson"
)
gdf_cyclone_track = gpd.read_file(
    "data/rsmc-tcwc/" + project_name + "/" + "rapid-exposure-forecast-cyclone-track.geojson"
)

gdf_cyclone_track_distance = gpd.read_file(
    "data/rsmc-tcwc/" + project_name + "/" + "rapid-exposure-forecast-track-distance.geojson"
)
# data
# df_regional_summary = pd.read_csv(
#     "data/" + "vanuatu" + "/" + "jtwc-forecast-regional-summary.csv"
# )
df_total_exposed = pd.read_csv(
    "data/rsmc-tcwc/" + project_name + "/" + "rapid-exposure-forecast-total-exposed-by-country.csv"
)

df_total_exposed_by_windspeed = pd.read_csv(
    "data/rsmc-tcwc/" + project_name + "/" + "rapid-exposure-forecast-total-by-windspeed-SK.csv"
)


# Base URL for the GeoServer WMS
GEOSERVER_URL = "https://nexus.pacificdata.org/geoserver/geonode/wms"


def get_info(feature=None):
    header = [html.B("Regional Exposure")]
    if not feature:
        return header + [html.P("N/A")]
    
    id = feature["id"]
    
    # print(id)

    return header + [
        html.P(gdf_regional_exposure.iloc[[int(id)]]["Region.Region"].values[0]),
        html.Div(
            [
                dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
                    f"""
        
        <table style='border: 1px'>
          <tr>
           <td>Buildings Exposed (#): </td/>
           <td>{gdf_regional_exposure.iloc[[int(id)]]["Exposed_Buildings"].values[0]}</td/>
          </tr>
          <tr>
           <td>Population Affected (#): </td/>
           <td>{gdf_regional_exposure.iloc[[int(id)]]["Exposed_Population"].values[0]}</td/>
          </tr>
          <tr>
           <td>Max Windspeed (km/h) : </td/>
           <td>{gdf_regional_exposure.iloc[[int(id)]]["Max_WindSpeed_kmph"].values[0]}</td/>
          </tr>
          <tr>
           <td>Min Windspeed (km/h) : </td/>
           <td>{gdf_regional_exposure.iloc[[int(id)]]["Min_WindSpeed_kmph"].values[0]}</td/>
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
                        ["TC Lola (Vanuatu)", "TC Meena (Cook Islands)", "TC Harold (Tonga)", "Samoa"],
                        "TC Harold (Tonga)",
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
                                    gdf_regional_exposure["geometry"].to_json(),
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
                            dl.GeoJSON(
                                data=json.loads(
                                    gdf_cyclone_track_distance["geometry"].to_json()
                                ),
                                zoomToBounds=True,
                                zoomToBoundsOnClick=True,
                                style=dict(
                                    weight=1,
                                    opacity=0.06,
                                    color="red",
                                    fillOpacity=0.04,
                                ),
                            ),
                            dl.GeoJSON(
                                data=json.loads(
                                    gdf_cyclone_track["geometry"].to_json()
                                ),
                                zoomToBounds=True,
                                zoomToBoundsOnClick=True,
                                style=dict(
                                    weight=3,
                                    opacity=1,
                                    color="grey",
                                    fillOpacity=0.5,
                                ),
                            ),                            
                            # dl.WMSTileLayer(
                            #     url=GEOSERVER_URL,
                            #     layers="geonode:ref_tc_meena_cook_islands_track_distance", 	
                            #     format="image/png",
                            #     transparent=True,
                            #     id="cyclone-track-distance-layer"

                            #     ),
                            info,
                        ],
                        zoom=6,
                        style={"height": "100vh"},
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
                                    df_total_exposed_by_windspeed,
                                    x='Danger',
                                    y="Buildings",
                                    histfunc="sum",
                                    color="Danger"
                                ).update_layout(
                                    xaxis_title="Maximum Windspeed Category",
                                    yaxis_title="No. Of Buildings Exposed",
                                    showlegend=False,
                                ),
                                style={"height": "30vh"}
                            ),
                            # bar chart - population per windspeed
                            html.B("Population Exposed by Windspeed"),
                            dcc.Graph(
                                figure=px.histogram(
                                    df_total_exposed_by_windspeed,
                                    x="Danger",
                                    y="Population",
                                    histfunc="sum",
                                    color="Danger",
                                ).update_layout(
                                    xaxis_title="Maximum Windspeed Category",
                                    yaxis_title="Population Exposed",
                                    showlegend=False
                                ),
                                style={"height": "30vh"},
                            ),
                            html.B("Exposed Building Value by Windspeed"),
                            dcc.Graph(
                                figure=px.bar(
                                    df_total_exposed_by_windspeed,
                                    x="Danger",
                                    y="Building_Value",
                                    # barmode="group",
                                    color="Danger",
                                ).update_layout(
                                    xaxis_title="Maximum Windspeed Category",
                                    yaxis_title="Exposed Building Value (USD)",
                                    showlegend=False
                                ),
                                style={"height": "40vh"},
                            ),
                        ]
                    )
                ),
            ]
        ),
        # dbc.Row(
        #     [
        #         html.B("Forecasted Total Exposed"),
        #         # bar chart - total value nation
        #         dash_table.DataTable(
        #             df_total_exposed.to_dict("records"),
        #             [{"name": i, "id": i} for i in df_total_exposed.columns],
        #         ),
        #     ]
        # ),
    ],
    # style={"textAlign": "center"},
    style={"backgroundColor": "#eaeded", "color": "black", "padding": "20px"}  # gray background and for the entire page
)


@callback(Output("info-tc", "children"), Input("map-regional-exposure", "hoverData"))
def info_hover(feature):
    return get_info(feature)
