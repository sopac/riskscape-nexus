import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import geopandas as gpd
import dash_leaflet as dl
import dash_leaflet.express as dlx
import json

dash.register_page(__name__)

project_name = "vanuatu-slr"

# load data single
gdf_admin_regional_impact = gpd.read_file(
    "data/" + project_name + "/" + "coastal-slr-risk-regional-impact.geojson"
)

gdf_regional_summary = gpd.read_file(
    "data/" + project_name + "/" + "coastal-slr-risk-regional-summary.geojson"
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
colorscale = ['red', 'yellow', 'green', 'blue', 'purple']  # rainbow
def get_info(feature=None):
    header = [html.B("Regional Summary")]
    if not feature:
        return header + [html.P("N/A")]
    id = feature["id"]
    #r = gdf_regional_summary.iloc[[int(id)]]["Region"].values[0]
    
    
    return header + [
        #html.P(id),
        html.P(gdf_regional_summary.iloc[[int(id)]]["Region"].values[0]),
        html.P("Change.Total_AAL : " + str(gdf_regional_summary.iloc[[int(id)]]["Change.Total_AAL"].values[0])),
        html.P("Change.Building_AAL : " + str(gdf_regional_summary.iloc[[int(id)]]["Change.Building_AAL"].values[0])),
        html.P("Change.Crops_AAL : " + str(gdf_regional_summary.iloc[[int(id)]]["Change.Crops_AAL"].values[0])),
        html.P("Change.Road_AAL : " + str(gdf_regional_summary.iloc[[int(id)]]["Change.Road_AAL"].values[0])),
        html.P("Change.Infrastructure_AAL : " + str(gdf_regional_summary.iloc[[int(id)]]["Change.Infrastructure_AAL"].values[0])),
        html.P("Change.Population_Exposed : " + str(gdf_regional_summary.iloc[[int(id)]]["Change.Population_Exposed"].values[0])),
        # html.B(feature["properties"]),
        # html.Br(),
        # "{:.3f} people / mi".format(feature["properties"]),
        # html.Sup("2"),
    ]


info = html.Div(
    children=get_info(),
    id="info",
    className="info",
    style={
        "position": "absolute",
        "top": "10px",
        "right": "10px",
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
                        ["cook-islands", "tonga", "samoa", "vanuatu"],
                        "vanuatu",
                        id="country-selection",
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
                        id="region-selection",
                    ),
                    width=6,
                ),
                html.Br(),
            ]
        ),
        dbc.Row(html.Br()),
        dbc.Row(
            [
                dbc.Col(
                    dl.Map(
                        [
                            # dl.TileLayer(url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"),
                            dl.TileLayer(),
                            dl.GeoJSON(
                                data=json.loads(
                                    gdf_regional_summary["geometry"].to_json()
                                ),
                                id="Region-Summary",
                                zoomToBounds=True,
                                zoomToBoundsOnClick=True,
                                style=dict(
                                    weight=2, opacity=1, color="red", fillOpacity=0.5, colorscale=colorscale,
                                ),
                            ),
                            info,
                        ],
                        zoom=6,
                        style={"height": "30vh"},
                        center=(
                            gdf_regional_summary.dissolve().centroid.y.values[0].item(),
                            gdf_regional_summary.dissolve().centroid.x.values[0].item(),
                        ),
                    )
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=px.bar(
                            gdf_regional_summary,
                            x="Region",
                            y=[
                                "Change.Total_AAL",
                                "Change.Building_AAL",
                                "Change.Crops_AAL",
                                "Change.Infrastructure_AAL",
                                "Change.Population_Exposed",
                            ],
                            barmode="group",
                            text_auto=False,
                            labels=["Total", "Building"],
                        )
                    )
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(),
                dbc.Col(),
            ]
        ),
    ],
    style={"textAlign": "center"},
)


@callback(Output("info", "children"), Input("Region-Summary", "hoverData"))
def info_hover(feature):
    return get_info(feature)
