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
from dash_bootstrap_templates import load_figure_template
from shapely import LineString

dash.register_page(__name__, external_stylesheets=[dbc.themes.SLATE])

load_figure_template('slate') # template for charts
project_name = "tc_harold_tonga"

color_map = ['#DBBF21', '#BD3539', '#57C560', '#F19502', '#81D6F6', '#5D6167', '#D169C1']

############################### LOAD AND PREPARE RISKSCAPE DATA ###############################

# tc meena data is for Cooks. 
# tc harold data is for Tonga
# tc lola data is for Vanuatu
# Below implemented some hard coded filtering to focus on specific country and tc. Eventually it should only choose the TC and show all countries for which there is data for it (?)


# data for the map
gdf_regional_exposure = gpd.read_file(
    # "data/" + "vanuatu" + "/" + "jtwc-forecast-regional-exposure.geojson"
    "data/rsmc-tcwc/" + project_name + "/" + "rapid-exposure-forecast-regional-impacts.geojson"
)
# filter for Tonga data
gdf_regional_exposure = gdf_regional_exposure[gdf_regional_exposure['Region.Country']=='Tonga']

gdf_cyclone_track = gpd.read_file(
    #"data/rsmc-tcwc/" + project_name + "/" + "rapid-exposure-forecast-cyclone-track.geojson"
    "data/rsmc-tcwc/" + project_name + "/" + "track.geojson"
)

gdf_cyclone_track_distance = gpd.read_file(
    #"data/rsmc-tcwc/" + project_name + "/" + "rapid-exposure-forecast-track-distance.geojson"
     "data/rsmc-tcwc/" + project_name + "/" + "track-distance.geojson"
)

df_total_exposed = pd.read_csv(
    "data/rsmc-tcwc/" + project_name + "/" + "rapid-exposure-forecast-total-exposed-by-country.csv"
)

df_total_exposed_by_windspeed = pd.read_csv(
    "data/rsmc-tcwc/" + project_name + "/" + "rapid-exposure-forecast-total-by-windspeed-SK.csv"
)


# Base URL for the GeoServer WMS
GEOSERVER_URL = "https://nexus.pacificdata.org/geoserver/geonode/wms"



############################### MAP FEATURE INFO BOX ###############################
def get_info(feature=None):
    header = [html.B("Regional Exposure")]
    if not feature:
        return header + [html.P("N/A")]
    
    id = feature["id"]

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


############################### LAYOUT COMPONENTS ##################################
### DROPDOWN - tropical cyclone
# define dropdown object
dropdown_tc =  dcc.Dropdown(
    options=["TC Lola (Vanuatu)", "TC Meena (Cook Islands)", "TC Harold (Tonga)", "Samoa"],
    value="TC Harold (Tonga)",
    id="country-select",
)


### MAP
map = dl.Map([
    dl.TileLayer(),
    dl.GeoJSON(
        data=json.loads(gdf_cyclone_track_distance["geometry"].to_json()),
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
        data=json.loads(gdf_cyclone_track["geometry"].to_json()),
        zoomToBounds=True,
        zoomToBoundsOnClick=True,
        style=dict(
            weight=3,
            opacity=1,
            color="grey",
            fillOpacity=0.5,
        ),
    ),
    dl.GeoJSON(
        id="map-regional-exposure",
        data=json.loads(gdf_regional_exposure["geometry"].to_json()),
        zoomToBounds=True,
        zoomToBoundsOnClick=True,
        style=dict(
            weight=2,
            opacity=1,
            color="red",
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
    style={"height": "70vh"},
    center=(
        gdf_regional_exposure.dissolve().centroid.y.values[0].item(),
        gdf_regional_exposure.dissolve().centroid.x.values[0].item(),
    ),
)


### CHART - no. of assets
chart_asset_no = dcc.Graph(
    figure=px.histogram(
        df_total_exposed_by_windspeed,
        x='Danger',
        y=["Buildings", "Population"],
        histfunc="sum",
        barmode="group"
    ).update_layout(
        xaxis_title="Maximum Windspeed Category",
        yaxis_title="No. Exposed",
        # paper_bgcolor ='rgb(252,252,252)',
        # font_color='rgb(20,20,20)',
        margin=dict(l=33, r=30, t=40, b=33),
        font=dict(size= 11),
        showlegend=True,
        legend_title_text='',
        legend=dict(
            orientation="h",
            yanchor='bottom',
            y=1.02,
            xanchor="right",
            x=1
        )
    ),
    style={"height": "30vh"}
)

### CHART - value of assets
chart_asset_value = dcc.Graph(
    figure=px.bar(
        df_total_exposed_by_windspeed,
        x="Danger",
        y=["Building_Value", "Road_Value", "Infrastructure_Value", "Crop_Value"],
        barmode="group",
        # hover_data={'exposure.UseType':False},
        labels={'variable': 'Asset', 'sum of value':'Count'}
    ).update_layout(
        xaxis_title="Maximum Windspeed Category",
        yaxis_title="Exposed Building Value (USD)",
        margin=dict(l=33, r=30, t=40, b=33),
        font=dict(size= 11),
        showlegend=True,
        legend_title_text='',
        legend=dict(
            orientation="h",
            yanchor='bottom',
            y=1.02,
            xanchor="right",
            x=1
        )
    ),
    style={"height": "30vh"},
)


############################### DEFINE LAYOUT ######################################
layout = html.Div(children=[
        # dbc.Row(
        #     dbc.Col(
        #         html.H3(
        #             "Rapid Exposure Forecase for Tropical Cyclone Scenarios",
        #             style={"textAlign": "center"},
        #         )
        #     )
        # ),
        # dbc.Row(html.Br()),
        dbc.Row([
                dbc.Col([
                    html.B("Tropical Cyclone : ")
                ], width=3),
                dbc.Col([
                    dropdown_tc
                ], width=6),
            ]),
        dbc.Row(html.Br()),
        dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.B("Regional Exposure and Track Path"),
                            map
                        ])
                    ])    
                ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            # bar chart - buildings per windspeed
                            html.B("No. Assets Exposed by Windspeed"),
                            chart_asset_no,
                        ])
                    ]),
                    html.Br(),
                    dbc.Card([
                        dbc.CardBody([
                            html.B("Value of Assets Exposed by Windspeed"),
                            chart_asset_value
                        ])
                    ])
                ])
            ]),
    ], style={"textAlign": "center", "padding": "10px"}
)


############################### CALLBACKS ##########################################
@callback(Output("info-tc", "children"), Input("map-regional-exposure", "hoverData"))
def info_hover(feature):
    return get_info(feature)
