import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import geopandas as gpd
import pandas as pd
import dash_leaflet as dl
import json
from dash_bootstrap_templates import load_figure_template


dash.register_page(__name__, external_stylesheets=[dbc.themes.SLATE])

load_figure_template('slate') # template for charts
project_name = "tonga_pdia_harold" # for selecting folder to read files

color_map = ['#DBBF21', '#BD3539', '#57C560', '#F19502', '#81D6F6', '#5D6167', '#D169C1']


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
dropdown_agg =  dcc.Dropdown(
    options=[
        {"label": "National", "value": "National"},
        {"label": "Regional", "value": "Regional"}
    ],
    value="National",
    id="aggregation-select",
    clearable=False
)


### DROPDOWN - hazard
dropdown_hazard = dcc.Dropdown(
    options=[
        {"label": "All hazards", "value": "All hazards"},
        {"label": "Coastal Inundation", "value": "Coastal Inundation"},
        {"label": "Wind", "value": "Wind"},
    ],
    value="All hazards",
    id="hazard-select",
    clearable=False
)


### MAP
# Base URL for the GeoServer WMS
GEOSERVER_URL = "https://nexus.pacificdata.org/geoserver/geonode/wms"

# temp track to avoid antemeridian issue during demo. Should otherwise be the one from PDIE project and/or PDIE one on GeoServer
gdf_cylone_track = gpd.read_file("data/rsmc-tcwc/tc_harold_tonga/track.geojson")

map = dl.Map([
    dl.LayersControl(
        [dl.BaseLayer(
            # default OSM
            dl.TileLayer(), 
            name='OpenStreetMap', 
            checked=True),
         dl.BaseLayer(
             # ESRI satellite imagery
             dl.TileLayer(
                 url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
                 attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'),
            name='ESRI satellite imagery',
            checked=False)
        ] +
        [dl.Overlay(
            # regional impact
            dl.GeoJSON(
                data=json.loads(gdf_regional_impacts["geometry"].to_json()),
                id="map-region-impact",
                zoomToBounds=True,
                zoomToBoundsOnClick=True,
                style=dict(
                    weight=2,
                    opacity=1,
                    color="red",
                    fillOpacity=0.5
                )), 
            name='Region impact', 
            checked=True),
         dl.Overlay(
            # cyclone track
            # dl.WMSTileLayer(
            #         url=GEOSERVER_URL,
            #         # layers="geonode:ref_tc_meena_cook_islands_cyclone_track",
            #         layers="geonode:to_cyclone_pdna_cyclone_track" ,	
            #         format="image/png",
            #         transparent=True,
            #         id="cyclone-track-layer"), 
            dl.GeoJSON(
                data=json.loads(gdf_cylone_track["geometry"].to_json()),
                style=dict(
                    weight=3,
                    opacity=1,
                    color="grey",
                    fillOpacity=0.5
                )
            ),
            name='Cyclone track',
            checked = False),
         dl.Overlay(
            # Coastal inundation extent
            dl.WMSTileLayer(
                url=GEOSERVER_URL,
                # layers="geonode:tc_lola_coastalinundation",
                layers="geonode:tc_harold_inundation_max_180",
                format="image/png",
                transparent=True,
                id="inundation-layer"),
            name = 'Coastal inundation extent',
            checked = False)
        ], id="lc"
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
                                    html.B("Total Value of exposed assets:"),
                                    dcc.Graph(
                                        id='chart-exposure',
                                        style={'height': '32vh'}
                                        )
                                ])
                            ], style={'height':'37vh'})
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.B("Total Damage of exposed assets:"),
                                    dcc.Graph(
                                        id='chart-damage',
                                        style={'height': '32vh'}
                                    )
                                ])
                            ], style={'height':'37vh'})
                        ])
                    ])
                ], width=3, style={"textAlign": "center"}),
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



############################### CALLBACKS ######################################################

### CHART - exposure (update based on aggregation level dropdown)
@callback(
    Output('chart-exposure', 'figure'),
    Input('aggregation-select', 'value')
)
def updateExposureChart(selected_aggregation):

    if selected_aggregation == 'National':
        fig = px.histogram(
            df_regional_summary_by_sector,
            x='Sector',
            y='Total_Exposed_Value',
            color='Region',
            histfunc="sum",
            labels={'Total_Exposed_Value': 'exposed value (USD)'},
            color_discrete_sequence=color_map
        )

    elif selected_aggregation == 'Regional':
        fig = px.histogram(
            df_regional_summary_by_sector,
            x='Region',
            y='Total_Exposed_Value',
            color='Sector',
            histfunc="sum",
            labels={'Total_Exposed_Value': 'exposed value (USD)'},
            color_discrete_sequence=color_map
        )

    fig.update_layout(
        yaxis_title='USD',
        margin=dict(l=22, r=20, t=20, b=33),
        font=dict(size= 11),
        showlegend=True,
        title=selected_aggregation,
        title_x=0.5
    )

    fig.update_xaxes(
    tickangle=45,
    tickfont={'size':12},
    title_font = {"size": 14}
    )

    fig.update_yaxes(
        title_font = {"size": 14}
    )
    
    return fig


## CHART - damage (update based on aggregation level and hazard dropdowns)
@callback(
    Output('chart-damage', 'figure'),
    [Input('aggregation-select', 'value'),
     Input("hazard-select", "value")]
)
def updateDamageChart(selected_aggregation, selected_hazard):

    if selected_hazard == 'All hazards':
        col_title = 'Total_Loss'
    elif selected_hazard == 'Coastal Inundation':
        col_title = 'Total_Coastal_Loss'
    elif selected_hazard == 'Wind':
        col_title = 'Total_Wind_Loss'


    if selected_aggregation == 'National':
        fig = px.histogram(
            df_regional_summary_by_sector,
            x='Sector',
            y=col_title,
            color='Region',
            histfunc="sum",
            color_discrete_sequence=color_map
        )

    elif selected_aggregation == 'Regional':
        fig = px.histogram(
            df_regional_summary_by_sector,
            x='Region',
            y=col_title,
            color='Sector',
            histfunc="sum",
            color_discrete_sequence=color_map
        )

    fig.update_layout(
        yaxis_title='USD',
        margin=dict(l=22, r=20, t=20, b=33),
        font=dict(size= 11),
        showlegend=True,
        title=selected_hazard,
        title_x=0.5
    )

    fig.update_xaxes(
        tickangle=45,
        tickfont={'size':12},
        title_font = {"size": 14}
        )
    
    fig.update_yaxes(
        title_font = {"size": 14}
    )
    
    return fig



