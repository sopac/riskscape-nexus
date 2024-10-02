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
import plotly.graph_objects as go


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
            dl.WMSTileLayer(
                    url=GEOSERVER_URL,
                    # layers="geonode:ref_tc_meena_cook_islands_cyclone_track",
                    layers="geonode:to_cyclone_pdna_cyclone_track" ,	
                    format="image/png",
                    transparent=True,
                    id="cyclone-track-layer"), 
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




############################### DASH CALLBACK FOR GRAPHS ###############################

# Update graphs based on selected cluster and aggregation level
# Cluster x National 
# Cluster x Regional

#### Exposure Value Pie Chart

@callback(
    Output("exposure", "figure"),
    Input("aggregation-select", "value")
)
def update_exposure_graph(selected_aggregation):

    # Check if both selections are made
    if not selected_aggregation:
        return go.Figure(
            data=[],
            layout=go.Layout(
                title={'text':"Total Exposed Value per sector ", 'font':{'size':15}},
                xaxis_title="Sector",
                yaxis_title="Value (USD)",
                annotations=[{
                    "text": "Select Aggregation Level <br> to view the data",
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
        
        # Create Bar Chart
        fig = go.Figure(
            data=[
                go.Bar(
                    x=df['Sector'],
                    y=df['Total_Exposed_Value'],
                    marker_color='indianred',
                )
            ],
            layout=go.Layout(
                title={
                    'text': 'Total Exposed Value per sector <br>- National Level',
                    'font': {
                        'size': 15  # Adjust the font size here
                    }
                },
                yaxis_title="Value (USD)",
                xaxis_title = 'Sector',
                template="plotly_white"
            )
        )
        return fig
    
    # Handle Regional Aggregation
    elif selected_aggregation.lower() == "regional":
        # if clickData is not None:            
        #     print(json.dumps(clickData))
        df = df_regional_summary_by_sector.copy()
        
        # Group by Region and Sector, then sum Total_Exposed_Value
        grouped_df = df.groupby(['Region', 'Sector'])['Total_Exposed_Value'].sum().unstack().fillna(0)
        
        # Create a trace for each sector
        traces = []
        for sector in grouped_df.columns:
            traces.append(
                go.Bar(
                    x=grouped_df.index,  # Regions on x-axis
                    y=grouped_df[sector],  # Total Exposed Values for each sector
                    name=sector
                )
            )
        
        # Create Stacked Bar Chart
        fig = go.Figure(
            data=traces,
            layout=go.Layout(
                title={
                    'text': 'Total Exposed Value per Sector <br> - Regional Level',
                    'font': {
                        'size': 15  # Adjust the font size here
                    }
                },
                barmode='stack',
                xaxis_title="Region",
                yaxis_title="Value (USD)",
                template="plotly_white"
            )
        )
        return fig
    






# Update damage summary graph based on selected hazard
# Hazard x National 
# Hazard x Regional

@callback(
    Output("loss-and-damage", "figure"),
    [Input("hazard-select", "value"),
     Input("aggregation-select", "value")
    ]
)
def update_damage_summary_graph(selected_hazard, selected_aggregation):
    # Validate that exactly one hazard is selected
    # if len(selected_hazards) != 1:

    row_title = ""

    if selected_hazard == "Wind":
        col_title = "Total_Wind_Loss"
    elif selected_hazard == "All hazards":
        col_title = "Total_Loss"
    elif selected_hazard == "Coastal Inundation":
        col_title = "Total_Coastal_Loss"
    else:
        return go.Figure(
            data=[],
            layout=go.Layout(
                title="Hazard Summary",
                annotations=[{
                    "text": "Select Aggregation Level <br> and hazard to view the data",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 10}
                }]
            )
        )

    # Handle National Aggregation
    if selected_aggregation.lower() == "national":
        if col_title in df_national_impact_by_sector.columns:                                                    
            
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=df_national_impact_by_sector['Sector'],
                        values=df_national_impact_by_sector[col_title],
                    )
                ],
                layout=go.Layout(
                    # title=f'Total Damage (USD) per sector <br> - National Level - {hazard}',
                    title = {'text':f"Total Damage per sector <br> - National Level - {selected_hazard}", 'font': {'size': 15}},
                    template="plotly_white"
                )
            )
            return fig
        else:
            return go.Figure(
                data=[],
                layout=go.Layout(
                    title = {'text':"Total Damage per sector", 'font': {'size': 15}},
                    annotations=[{
                        "text": "Data not available <br> for the selected hazard.",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 10}
                    }]
                )
            )
        
    # Handle Regional Aggregation
    elif selected_aggregation.lower() == "regional":
        # Check if the row title is present in the index
        if col_title in df_regional_summary_by_sector.columns:
            df = df_regional_summary_by_sector.copy()
        # Group by Region and Sector, then sum Total_Exposed_Value
            grouped_df = df.groupby(['Region', 'Sector'])[col_title].sum().unstack().fillna(0)
        
            # Create a trace for each sector
            traces = []
            for sector in grouped_df.columns:
                traces.append(
                    go.Bar(
                        x=grouped_df.index,  # Regions on x-axis
                        y=grouped_df[sector],  # Total Exposed Values for each sector
                        name=sector
                    )
                )
        
            # Create Stacked Bar Chart
            fig = go.Figure(
                data=traces,
                layout=go.Layout(
                    title={'text': f'Total Damage per Sector <br> - Regional Level - {selected_hazard}', 'font': {'size': 15}},
                    barmode='stack',
                    xaxis_title="Region",
                    yaxis_title="Damage (USD)",
                    template="plotly_white"
                )
            )
        return fig

    else:
        # return go.Figure(
        #     data=[],
        #     layout=go.Layout(
        #         title={'text': 'Total Damage per Sector', 'font': {'size': 15}},
        #         annotations=[{
        #             "text": "Invalid aggregation level.",
        #             "xref": "paper",
        #             "yref": "paper",
        #             "showarrow": False,
        #             "font": {"size": 14}
        #         }]
        #     )
        # )
        return go.Figure(
            data=[],
            layout=go.Layout(
                title={'text':"Total Damage per sector", 'font': {'size': 15}},
                xaxis_title="Hazard",
                yaxis_title="Damage (USD)",
                annotations=[{
                    "text": "Please select only one hazard.",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 10}
                }]
            )
        )



##### streamlining attempt before Tonga demo
# load_figure_template('slate')


# fig_exposure = px.histogram(
#             df_national_impact_by_sector,
#             x='Sector',
#             y='Total_Exposed_Value',
#             color='Sector',
#             histfunc="sum",
#             hover_name='Sector',
#             hover_data={'Sector':False},
#             labels={'Total_Exposed_Value': 'exposed value (USD)'}
#         ).update_layout(
#             yaxis_title='Total Value of exposed assets (USD)',
#             margin=dict(l=25, r=25, t=20, b=33),
#             font=dict(size= 11),
#             showlegend=False,
#         )

# chart_exposure=dcc.Graph(
#     figure=fig_exposure, 
#     id='chart-exposure',
#     style={'height': '35vh'}
#     )


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
                                    # html.P('Please select an aggregation level to view the chart'),
                                    # chart_exposure
                                    dcc.Graph(
                                        id='exposure',
                                        style={'height': '33vh'}
                                    )
                                ])
                            ], style={'height':'37vh'})
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Graph(
                                        id='loss-and-damage',
                                        style={'height': '33vh'}
                                    )
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







############## callbacks

# ### update exposure chart based on aggregation level dropdown
# @callback(
#     Output('chart-exposure', 'children'),
#     Input('aggregation-select', 'value')
# )
# def updateExposureChart(value):
#     if value == 'National':
#         fig_exposure = px.bar(
#             df_national_impact_by_sector,
#             x='Sector',
#             y='Total_exposed_Value'
#         )
#     chart_exposure=dcc.Graph(figure=fig_exposure)
#     return chart_exposure