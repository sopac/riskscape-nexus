import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import geopandas as gpd
import dash_leaflet as dl
import json
from dash_bootstrap_templates import load_figure_template

dash.register_page(__name__, external_stylesheets=[dbc.themes.SLATE])

# Set data folder for RiskScape outputs:
project_name = "vanuatu" 
# """Vanuatu has a seperate flood layer per region,
# while Samoa has one for the whole country (or at least the areas covered)"""


############################### LOAD DATA ###############################
#load regional impacts
gdf_regional_impacts = gpd.read_file(
    "data/" + project_name + "/" + "fluvial-static-inundation-regional-impacts.geojson"
)

#load impact to buildings
gdf_building_impacts = gpd.read_file(
    "data/" + project_name + "/" + "fluvial-static-inundation-building-impacts.geojson"
)

############################### LAYOUT COMPONENTS #######################
### DROPDOWN - region
# list of regions for region selection dropdown
regions = gdf_regional_impacts["Region"].tolist()
regions.sort()
regions = ['All'] + regions
# define dropdown object
dropdown_region =  dcc.Dropdown(
    options=[
        {"label": region, "value": region} for region in regions
    ],
    value="",
    id="region-select"
)


### DROPDOWN - ari
    # define dropdown object
dropdown_ari = dcc.Dropdown(
    options=[
        {"label":'2 years', "value":'2'},
        {"label":'5 years', "value":'5'},
        {"label":'10 years', "value":'10'},
        {"label":'50 years', "value":'50'},
        {"label":'100 years', "value":'100'},
        {"label":'200 years', "value":'200'},
    ],
    value="",
    id="region-select-fluvial"
)

### MAP
map = dl.Map([
        dl.TileLayer(),
        dl.GeoJSON(
            data=json.loads(gdf_regional_impacts["geometry"].to_json()),
            id='map_fluvial_impact',
            zoomToBounds=True,
            zoomToBoundsOnClick=True,
            style=dict(
                weight=2,
                opacity=1,
                color="red",
                fillOpacity=0.5
            )
        )
    ],
    style={'height': '45vh'}, #define style for the map
    zoom=6,
    center=(
        gdf_regional_impacts.dissolve().centroid.y.values[0].item(),
        gdf_regional_impacts.dissolve().centroid.x.values[0].item(),
    ),
)


### TEXT BOXES - function called in layout
def draw_text(input_label, input_value):

    return html.Div([
            dbc.Card([
                dbc.CardBody([
                        html.Div([
                            html.H6(input_label),
                            html.H4(input_value),
                        ], style={'textAlign': 'center', 'height':'8vh'}) 
                ]),
            ])
        ], style ={'marginTop':'10px'})


### CHART - buildings prep
# additional work: filter on region, filter on ARI based on user selection. Now hardcoded for ARI 5
# manipulate dataframe to display count of buildings by use type per ARI scenario and region
gdf_building_impacts_notnull = gdf_building_impacts[gdf_building_impacts['Impact.ARI5.Flood_Depth'].notnull()]
# group by building use type
grouped = gdf_building_impacts_notnull.groupby('exposure.UseType')
# build dataframe with require stats for building pie chart and informing pop-up
df_building_impacts_summary = pd.DataFrame()
df_building_impacts_summary['count'] = grouped.count()['geometry']
df_building_impacts_summary['exposureValue_sum'] = grouped.sum('exposure.Value')['exposure.Value']

# load_figure_template('slate')
# load_figure_template('darkly')
load_figure_template('seaborn')

chart_buildings = px.pie(
    df_building_impacts_summary, 
    values='count', 
    names=df_building_impacts_summary.index,
    hover_name=df_building_impacts_summary.index,
    # hover_data=['count', 'exposureValue_sum'], # needs more attention
    # labels={'exposureValue_sum': 'Total exposure (USD)'},
    # title='Share of exposed buildings by use type for selected region and Average Recurrence Interval',
    hole=.3,
    # color_discrete_sequence=px.colors.sequential.Rainbow,
    # template='plotly_dark'
)

chart_buildings_fig = dcc.Graph(figure=chart_buildings, style={'height': '30vh'})


### CHART - roads
chart_roads = html.P('roads pie')


### CHART - card
def draw_chart_card(chart, title):
        return html.Div([
            dbc.Card([
                dbc.CardBody([
                        html.Div([
                            html.H6(title),
                            chart,
                        ], style={'height':'33vh'}) 
                ]),
            ])
        ], style ={'marginBottom':'10px'})


## CARDS in layout
cards = html.Div(children=[
    
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.P("Region:"),
                            dropdown_region,
                            html.Br(),
                            html.P('Average Recurrence Interval:'),
                            dropdown_ari,
                            html.Br(),
                        ])
                    ]),
                    dbc.Card([
                        dbc.CardBody([
                            html.P('Rainfall event duration: 12h'),
                            html.P('Max. rain depth dynamic text'),
                        ])
                    ]),
                ], width=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            map
                        ])
                    ]),
                    # html.Br(),
                    dbc.Row([
                        dbc.Col([
                            draw_text('Total Loss (USD):', '123 test')
                        ]),
                        dbc.Col([
                            draw_text('Exposed Buildings (#):', '123 test')                          
                        ]),
                        dbc.Col([
                            draw_text('Exposed Schools (#):', '123 test')
                        ]) 
                    ]),
                    dbc.Row([
                        dbc.Col([
                            draw_text('Exposed Health Facilities (#):', '123 test')
                        ]),
                        dbc.Col([
                            draw_text('Exposed Roads (km):', '123 test')                          
                        ]),
                        dbc.Col([
                            draw_text('Exposed People (#):', '123 test')
                        ]) 
                    ]),
                ], width=5),
                dbc.Col([
                    draw_chart_card(chart_buildings_fig, 'Share of exposed buildings by use type for selected region and Average Recurrence Interval'),
                    draw_chart_card(chart_buildings_fig, 'Share of exposed roads by use type for selected region and Average Recurrence Interval')
                ])
            ])  
    ])

############################### DEFINE LAYOUT ###########################
layout = html.Div(children=[

cards
    
 
]) 

