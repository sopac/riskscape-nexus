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
from dash_bootstrap_templates import load_figure_template


dash.register_page(__name__, external_stylesheets=[dbc.themes.SLATE])

project_name = "tonga_pdia_harold"

############################### LOAD AND PREPARE RISKSCAPE DATA ###############################

#  datasets  #
#load regional impacts
gdf_regional_impacts = gpd.read_file("data/" + project_name + "/" + "cyclone_pdna_regional-impacts.geojson")


#  CSV's  #
#load impact by asset type
df_impact_by_asset_type = pd.read_csv("data/" + project_name + "/" + "cyclone_pdna_impact-by-asset-type.csv")
# # set index
df_impact_by_asset_type.set_index('Asset', inplace=True)

#load national impacts by sector
df_national_impact_by_sector = gpd.read_file("data/" + project_name + "/" + "cyclone_pdna_impact-by-sector.csv")

#load national summary
df_national_summary = pd.read_csv("data/" + project_name + "/" + "cyclone_pdna_national-summary.csv")

#load regional summary by sector
df_regional_summary_by_sector = gpd.read_file("data/" + project_name + "/" + "cyclone_pdna_regional-summary-by-sector.csv")




############################### LAYOUT COMPONENTS ##############################################
### DROPDOWN - aggregation level
# define dropdown object
dropdown_agg =  dcc.Dropdown(
    options=[
        {"label": "National", "value": "National"},
        {"label": "Regional", "value": "Regional"}
    ],
    value="",
    id="aggregation-select",
)


### DROPDOWN - hazard
# define the dropdown object
dropdown_hazard = dcc.Dropdown(
    options=[
        {"label": "All hazards", "value": "All hazards"},
        {"label": "Coastal Inundation", "value": "Coastal Inundation"},
        {"label": "Wind", "value": "Wind"},
    ],
    value="",
    id="hazard-select"
)


### MAP
# Base URL for the GeoServer WMS
GEOSERVER_URL = "https://nexus.pacificdata.org/geoserver/geonode/wms"

map = dl.Map([
    dl.LayersControl(
        [dl.BaseLayer(dl.TileLayer(), name='OpenStreetMap', checked=True)] +
        [dl.Overlay(dl.GeoJSON(data=json.loads(gdf_regional_impacts["geometry"].to_json()),
            id="map-region-impact",
            zoomToBounds=True,
            zoomToBoundsOnClick=True,
            style=dict(
                weight=2,
                opacity=1,
                color="red",
                fillOpacity=0.5
            )), name='Region impact', checked=True)],
            id="lc"
    )
    ],
    style={"height": "70vh"},
    zoom=6,
    center=(
        gdf_regional_impacts.dissolve().centroid.y.values[0].item(),
        gdf_regional_impacts.dissolve().centroid.x.values[0].item()
        )
)



############################### DASHBOARD LAYOUT ###############################################
layout = html.Div(children=[
        dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.P("Select an aggregation level for the charts:"),
                            dropdown_agg,
                            html.Br(),
                            html.P('Select a hazard for the charts:'),
                            dropdown_hazard
                        ])
                    ])
                ], width=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                             map,
                             html.Div(id="log")           
                        ])         
                    ], style={"height": "74vh"})
                ], width=4),
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.P('Please select an aggregation level to view the chart')
                                ])
                            ], style={'height':'37vh'})
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.P('Please select an aggregation level and hazard to view the chart')
                                ])
                            ], style={'height':'37vh'})
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    dbc.Row([
                                        html.B('# of Assets Exposed to All Hazards - National Level', style={'text-align': 'center'})
                                    ]),
                                    html.Br(),
                                    dbc.Row([
                                        dbc.Col([html.P('Population: ', style={'line-height':'0.5'}),
                                                 html.P('Infrastructure: ', style={'line-height':'0.5'}),
                                                 html.P('Buildings: ', style={'line-height':'0.5'}),                                               
                                                 html.P('Evacuation Centres: ', style={'line-height':'0.5'}),
                                                 html.P('Health Facilties: ', style={'line-height':'0.5'}),
                                                 html.P('Schools: ', style={'line-height':'0.5'}),
                                                 ]),
                                        dbc.Col([html.P(df_national_summary["Buildings_Exposed_To_Any_Hazard"], style={'line-height':'0.5'}),
                                                 html.P(df_national_summary["Population_Exposed_To_Any_Hazard"], style={'line-height':'0.5'}),
                                                 html.P(df_national_summary["Exposed_Infrastructure"], style={'line-height':'0.5'}),
                                                 html.P(df_national_summary["Exposed_Evacuation_Centres"], style={'line-height':'0.5'}),
                                                 html.P(df_national_summary["Exposed_Health_Facilties"], style={'line-height':'0.5'}),
                                                 html.P(df_national_summary["Exposed_Schools"], style={'line-height':'0.5'})
                                                 ]),
                                    ])
                                ], style={'height':'30vh'})
                            ])
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    dbc.Row([
                                        html.B('USD Asset Damage from All Hazards - National Level', style={'text-align': 'center'})
                                    ]),
                                    html.Br(),
                                    dbc.Row([
                                        dbc.Col([html.P('Airports: ', style={'line-height':'0.5'}),
                                                 html.P('Bridges: ', style={'line-height':'0.5'}),
                                                 html.P('Crops: ', style={'line-height':'0.5'}),
                                                 html.P('Evacuation Centres: ', style={'line-height':'0.5'}),
                                                 html.P('Health Facilities: ', style={'line-height':'0.5'}),
                                                 html.P('Ports: ', style={'line-height':'0.5'}),
                                                 html.P('Power: ', style={'line-height':'0.5'}),
                                                 html.P('Roads: ', style={'line-height':'0.5'}),
                                                 html.P('Schools: ', style={'line-height':'0.5'}),
                                                 html.P('Telecommunication: ', style={'line-height':'0.5'}),
                                                 html.P('Water: ', style={'line-height':'0.5'}),
                                                 ]),
                                        dbc.Col([html.P(df_impact_by_asset_type.loc['Airport', 'Total_Loss'], style={'line-height':'0.5'}),
                                                 html.P(df_impact_by_asset_type.loc['Bridge', 'Total_Loss'], style={'line-height':'0.5'}),
                                                 html.P(df_impact_by_asset_type.loc['Crop', 'Total_Loss'], style={'line-height':'0.5'}),
                                                 html.P(df_impact_by_asset_type.loc['Evacuation Centre', 'Total_Loss'], style={'line-height':'0.5'}),
                                                 html.P(df_impact_by_asset_type.loc['Health Facility', 'Total_Loss'], style={'line-height':'0.5'}),
                                                 html.P(df_impact_by_asset_type.loc['Port', 'Total_Loss'], style={'line-height':'0.5'}),
                                                 html.P(df_impact_by_asset_type.loc['Power', 'Total_Loss'], style={'line-height':'0.5'}),
                                                 html.P(df_impact_by_asset_type.loc['Road', 'Total_Loss'], style={'line-height':'0.5'}),
                                                 html.P(df_impact_by_asset_type.loc['School', 'Total_Loss'], style={'line-height':'0.5'}),
                                                 html.P(df_impact_by_asset_type.loc['Telecommunication', 'Total_Loss'], style={'line-height':'0.5'}),
                                                 html.P(df_impact_by_asset_type.loc['Water', 'Total_Loss'], style={'line-height':'0.5'}),
                                                 ]),
                                    ])
                                ], style={'height':'44vh'})
                            ])
                        ])
                    ])
                ])
        ])
])





