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

load_figure_template('slate') # template for charts
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

#load impact to roads
gdf_road_impacts = gpd.read_file(
    "data/" + project_name + "/" + "fluvial-static-inundation-road-impacts.geojson"
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
    id="region-select-fluvial"
)


### DROPDOWN - ari
    # define dropdown object
dropdown_ari = dcc.Dropdown(
    options=[
        {"label":'10 years', "value":'10'},
        {"label":'50 years', "value":'50'},
        {"label":'100 years', "value":'100'}
    ],
    value="10",
    id="ari-select-fluvial",
    clearable=False
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


### CHART - buildings
    # additional work: filter on region, filter on ARI based on user selection. Now hardcoded for ARI 5
    # manipulate dataframe to display count of buildings by use type per ARI scenario and region
gdf_building_impacts_notnull = gdf_building_impacts[gdf_building_impacts['Impact.ARI5.Flood_Depth'].notnull()]
    # group by building use type
grouped = gdf_building_impacts_notnull.groupby(['Region','exposure.UseType'])
    # build dataframe with require stats for building pie chart and informing pop-up
df_building_impacts_summary = pd.DataFrame()
df_building_impacts_summary['count'] = grouped.count()['geometry']
df_building_impacts_summary['exposureValue_sum'] = grouped.sum('exposure.Value')['exposure.Value']
df_building_impacts_summary.reset_index(inplace=True)


chart_buildings = px.bar(
    df_building_impacts_summary, 
    x='exposure.UseType', 
    y='exposureValue_sum',
    color='Region',
    hover_name='exposure.UseType',
    hover_data={'exposure.UseType':False},
    labels={'exposureValue_sum': 'Total exposure (USD)', 'exposure.UseType':'Building use type'},
    # category_orders={'exposure.UseType':pd.Series(list(df_building_impacts_summary['exposure.UseType'])).drop_duplicates().to_list()}, # NOT WORKING
    # color_discrete_sequence=px.colors.sequential.Rainbow,
    # template='seaborn'
)

chart_buildings.update_layout(
    paper_bgcolor ='rgb(252,252,252)',
    font_color='rgb(20,20,20)',
    margin=dict(l=30, r=20, t=40, b=30),
    font=dict(size= 12)
    )

chart_buildings_fig = dcc.Graph(figure=chart_buildings, style={'height': '30vh'})


### CHART - roads
    # additional work: filter on region, filter on ARI based on user selection. Now hardcoded for ARI 5
    # manipulate dataframe to display count of buildings by use type per ARI scenario and region
gdf_road_impacts_notnull = gdf_road_impacts[gdf_road_impacts['Impact.ARI5.Flood_Depth'].notnull()]
    # group by building use type
grouped = gdf_road_impacts_notnull.groupby(['Region','exposure.UseType'])
    # build dataframe with require stats for building pie chart and informing pop-up
df_road_impacts_summary = pd.DataFrame()
df_road_impacts_summary['count'] = grouped.count()['geometry']
df_road_impacts_summary['exposureValue_sum'] = grouped.sum('exposure.Value')['exposure.Value']
df_road_impacts_summary.reset_index(inplace=True)

chart_roads = px.bar(
    df_road_impacts_summary, 
    x='exposure.UseType', 
    y='exposureValue_sum',
    color='Region',
    hover_name='exposure.UseType',
    hover_data={'exposure.UseType':False},
    labels={'exposureValue_sum': 'Total exposure (USD)', 'exposure.UseType':'Building use type'},
    # category_orders={'exposure.UseType':pd.Series(list(df_road_impacts_summary['exposure.UseType'])).drop_duplicates().to_list()}, # NOT WORKING
    # color_discrete_sequence=px.colors.sequential.Rainbow,
    # template='seaborn'
)

chart_roads.update_layout(
    paper_bgcolor ='rgb(252,252,252)',
    font_color='rgb(20,20,20)',
    margin=dict(l=30, r=20, t=40, b=30),
    font=dict(size= 12)
    )

chart_roads_fig = dcc.Graph(figure=chart_roads, style={'height': '30vh'})


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
                            html.B('Rainfall event duration:'),
                            html.P('12h'),
                            html.B('Max rain depth:'),
                            dbc.Row(id='rain_depth')
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
                    draw_chart_card(chart_buildings_fig, 'Share of exposed buildings by use type for selected Average Recurrence Interval'),
                    draw_chart_card(chart_roads_fig, 'Share of exposed roads by use type for selected Average Recurrence Interval')
                ])
            ])  
    ])

############################### DEFINE LAYOUT ###########################
layout = html.Div(children=[

cards
    
 
]) 

############################## CALLBACKS ################################

# callback rain depth card
@callback(
      Output(component_id='rain_depth', component_property='children'),
      Input(component_id='ari-select-fluvial', component_property='value')
)
def update_rain_depth_card(ari_value):
      rain_depths={'vanuatu':{'10':'197.69', '50':'305.76', '100':'364.17'}}
      rain_depth_text = f'{rain_depths[project_name][ari_value]}mm'

      return dbc.Row(html.P(rain_depth_text))

# # callback text cards
# @callback(
#       Output(component_id='stats', component_property='children'),
#       [Input('region-select-fluvial', 'value'),
#        Input('ari-select-fluvial', 'value')]
# )
# def update_output_stats(region_value, ari_value):
#     #  ari_col_names = {'10':'ARI', '50':'', '100':''}
           



#      filtered_df = gdf_regional_impacts[(gdf_regional_impacts['Region']==region_value) & gdf_regional_impacts]

