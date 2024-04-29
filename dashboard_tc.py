from greppo import app
import geopandas as gpd
import pandas as pd
import numpy as np
from random import randrange

project_name = app.select(
    name="Cyclone", options=["Lola", "Pam", "Winston"], default="Lola"
)

app.display(
    name="title", value="PARTneR-2 Tropical Cyclone Dashboard [" + project_name + "]"
)
app.display(
    name="description",
    value="PARTneR-2: Pacific Risk Tool for Resilience - Tropical Cyclone Dasboards",
)

text_1 = """
## Pacific Risk Tool for Resilience
![logo](https://niwa.co.nz/sites/default/files/styles/portrait/public/PARTneR-2_partner%20logo%20panel.jpg)
The PARTneR–2 project is funded by the New Zealand Ministry of Foreign Affairs and Trade (MFAT). It is jointly delivered by the Pacific Community (SPC) and NIWA, in collaboration with the partner countries.
"""

app.display(name="text-1", value=text_1)

# app.display(name='text-2', value='The following displays the count of polygons, lines and points as a barchart.')

# base layers
app.base_layer(
    name="OSM",
    visible=True,
    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    subdomains=None,
    attribution="Pacific Community (SPC)",
)

app.base_layer(
    name="CartoDb",
    visible=False,
    url="https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/{z}/{x}/{y}@2x.png",
    subdomains=None,
    attribution="Pacific Community (SPC)",
)

app.base_layer(
    name="Satellite",
    visible=False,
    url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    subdomains=None,
    attribution="Pacific Community (SPC)",
)

app.base_layer(
    name="Topographic",
    visible=False,
    url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    subdomains=None,
    attribution="Pacific Community (SPC)",
)

# base spatial data
project_name = "rsmc-tcwc"
gdf_regional_exposure = gpd.read_file(
    "data/" + project_name + "/" + "rapid-exposure-forecast-regional-exposure.geojson"
)

gdf_cyclone_track = gpd.read_file(
    "data/" + project_name + "/" + "rapid-exposure-forecast-cyclone-track.geojson"
)

gdf_track_distance = gpd.read_file(
    "data/" + project_name + "/" + "rapid-exposure-forecast-track-distance.geojson"
)

gdf_wind_swaths = gpd.read_file(
    "data/" + project_name + "/" + "rapid-exposure-forecast-wind-swaths.geojson"
)

# base tabular data
df_regional_summary = pd.read_csv(
    "data/" + project_name + "/" + "rapid-exposure-forecast-regional-summary.csv"
)

# map layers


# bar chart (total population per windspeed)

# bar chart (total buildings per windspeed)

# bar chart (total value per windspeed)
