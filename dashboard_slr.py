from greppo import app
import geopandas as gpd
import numpy as np
from random import randrange

#project_name = "cook-islands"
project_name = app.select(name="Country", options=["cook-islands", "tonga", "samoa"], default="cook-islands")

app.display(name="title", value="PARTneR-2 Sea Level Rise Dashboard [" + project_name + "]")
app.display(
    name="description", value="PARTneR-2: Pacific Risk Tool for Resilience - Sea Level Rise Dasboards"
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

# load data single
gdf_admin_regional_impact = gpd.read_file(
    "data/" + project_name + "/" + "coastal-slr-risk-admin1-regional-impact.geojson"
)

gdf_regional_summary = gpd.read_file(
    "data/" + project_name + "/" + "coastal-slr-risk-regional-summary.geojson"
)

gdf_national_loss_curve = gpd.read_file(
    "data/" + project_name + "/" + "coastal-slr-risk-national-loss-curve.geojson"
)

# gdf_buildings_impact = gpd.read_file(
#    "data/" + project_name + "/" + "coastal-slr-risk-buildings-impact.geojson"
# )


# spatial filter
regions = gdf_regional_summary["Region.Region"].tolist()
regions.sort()
filter_region = app.select(name="Filter By Island", options=regions, default="*")

gdf_regional_summary_filtered = gdf_regional_summary
gdf_admin_regional_impact_filtered = gdf_admin_regional_impact
if filter_region != "*":
    gdf_regional_summary_filtered = gdf_regional_summary[
        gdf_regional_summary["Region.Region"] == filter_region
    ]
    gdf_admin_regional_impact_filtered = gdf_admin_regional_impact[
        gdf_admin_regional_impact["Region"] == filter_region
    ]


#bar chart (total loss change)
bar_change_gdf = gdf_regional_summary_filtered[
    [
        "Region.ID",
        "Region.Region",
        "Change.Total_AAL",
        "Change.Building_AAL",
        "Change.Crops_AAL",
        "Change.Infrastructure_AAL",
        "Change.Average_Annual_Population_Exposed",
    ]
]

app.bar_chart(
    name="AAL Change by Island",
    description="Average Annual Loss Change",
    x = bar_change_gdf["Region.Region"].tolist(),
    y = [bar_change_gdf['Change.Total_AAL'].tolist(), bar_change_gdf['Change.Building_AAL'].tolist(), bar_change_gdf['Change.Crops_AAL'].tolist(), bar_change_gdf['Change.Infrastructure_AAL'].tolist(), bar_change_gdf['Change.Average_Annual_Population_Exposed'].tolist()],
    label=['Total', 'Building', 'Crops', 'Infastructure', 'Population'],
    color=["rgb(255, 0, 0)", "rgb(0, 0, 255)", "rgb(0, 255, 0)", "rgb(100, 50, 150)", "rgb(200, 50, 150)"],
)

#bar char (loss by scenario)
gdf_bar_scenario = gdf_admin_regional_impact_filtered

gdf_bar_scenario.columns = gdf_bar_scenario.columns.str.replace("SLR_", "")
gdf_bar_scenario.columns = gdf_bar_scenario.columns.str.replace("cm_ARI100", "")

s_list = []
s_list.append("Region")
for i in ["0", "50", "100", "150"]:
    s_list.append(i + ".Total.Loss")
    s_list.append(i + ".Buildings.Loss")
    s_list.append(i + ".Crops.Loss")
    s_list.append(i + ".Infrastructure.Loss")
    s_list.append(i + ".Population.Loss")
    
gdf_bar_scenario = gdf_bar_scenario[s_list]

builder = []
for i in ["0","50", "100", "150"]:
    builder.append(gdf_bar_scenario[i + ".Total.Loss"].tolist())
    builder.append(gdf_bar_scenario[i + ".Buildings.Loss"].tolist())
    builder.append(gdf_bar_scenario[i + ".Crops.Loss"].tolist())
    builder.append(gdf_bar_scenario[i + ".Infrastructure.Loss"].tolist())
    builder.append(gdf_bar_scenario[i + ".Population.Loss"].tolist())

#format label
s_list.remove("Region")
#s_list = [sub.replace('0.', '0m ') for sub in s_list]
#s_list = [sub.replace('50.', '0.5m ') for sub in s_list]
#s_list = [sub.replace('100.', '1m ') for sub in s_list]
#s_list = [sub.replace('150.', '1/5m ') for sub in s_list]
s_list = [sub.replace('0.', '0 cm.') for sub in s_list]
s_list = [sub.replace('.', ' ') for sub in s_list]
#s_list = [sub.replace('Loss', '') for sub in s_list]


app.bar_chart(
    name="AAL Scenario by Island",
    description="Average Annual Loss by Scenario",
    x = gdf_bar_scenario["Region"].tolist(),
    #y = [bar_change_gdf['Change.Total_AAL'].tolist(), bar_change_gdf['Change.Building_AAL'].tolist(), bar_change_gdf['Change.Crops_AAL'].tolist(), bar_change_gdf['Change.Infrastructure_AAL'].tolist(), bar_change_gdf['Change.Average_Annual_Population_Exposed'].tolist()],
    y=builder,
    #label=['Total', 'Building', 'Crops', 'Infastructure', 'Population'],
    label=s_list,
    color=["rgb(255, 0, 0)", "rgb(0, 0, 255)", "rgb(0, 255, 0)", "rgb(100, 50, 150)", "rgb(200, 50, 150)","rgb(255, 0, 0)", "rgb(0, 0, 255)", "rgb(0, 255, 0)", "rgb(100, 50, 150)", "rgb(200, 50, 150)","rgb(255, 0, 0)", "rgb(0, 0, 255)", "rgb(0, 255, 0)", "rgb(100, 50, 150)", "rgb(200, 50, 150)","rgb(255, 0, 0)", "rgb(0, 0, 255)", "rgb(0, 255, 0)", "rgb(100, 50, 150)", "rgb(200, 50, 150)"],
)




# region styling
gdf_regional_summary["Region.ID"] = gdf_regional_summary["Region.ID"].astype(int)
bin_list_id = gdf_regional_summary["Region.ID"].tolist()
bin_list_id.sort()

gdf_regional_summary["Change.Total_AAL"] = gdf_regional_summary[
    "Change.Total_AAL"
].astype(int)
bin_list_change = gdf_regional_summary_filtered["Change.Total_AAL"].tolist()
bin_list_change.sort()

region_style_by_id = {
    "key_on": "Region.ID",
    "bins": bin_list_id,
    "palette": "Dark2",
}

region_style_by_change_total_aal = {
    "key_on": "Change.Total_AAL",
    "bins": bin_list_change,
    "palette": "Reds",
}

# add layers
app.vector_layer(
    data=gdf_regional_summary_filtered,
    name="Regional Summary",
    description="Regional Summary Description (TBD)",
    style={"choropleth": region_style_by_change_total_aal},
    visible=True,
)

app.vector_layer(
    data=gdf_admin_regional_impact,
    name="Admin Regional Impact",
    description="Admin Regional Impact Description (TBD)",
    style={"fillColor": "blue"},
    visible=False,
)

# national loss curve line chart (filtered by ssp)
years = gdf_national_loss_curve["Year"].tolist()
years = list(set(years))
years.sort()

# ssp filter
ssp_list = gdf_national_loss_curve["Scenario"].tolist()
ssp_list = list(set(ssp_list))
ssp_list.sort()

ssp_select = app.multiselect(
    name="Select SSP Scenario",
    options=ssp_list,
    # default=["ssp119 (medium confidence) p5"],
    default=["5"],
)

# default filter by percentile 5
nl_df = gdf_national_loss_curve.loc[gdf_national_loss_curve["Percentile"] == 5]

if ssp_select != ['5']:
    nl_df = gdf_national_loss_curve[gdf_national_loss_curve['Scenario'].isin(ssp_select)]

label_list = []
color_list = []
scenario_list = nl_df["Scenario"].tolist()
scenario_list = list(set(scenario_list))
scenario_list.sort()

for s in scenario_list:
    label_list.append(s)
    color_list.append(
        "rgb("
        + str(randrange(255))
        + ", "
        + str(randrange(255))
        + ", "
        + str(randrange(255))
    )

data_list = []
year_data = []

for s in scenario_list:
    sc_nl_df = nl_df.loc[nl_df["Scenario"] == s]

    scenario_data_list = []
    for year in years:

        yr_nl_df = sc_nl_df.loc[sc_nl_df["Year"] == year]
        year_data = yr_nl_df["Total_AAL"]  # .astype(float)
        val = year_data.values.tolist()
        if len(val) == 0:
            val = [0.0]
        val = val[0]
        scenario_data_list.append(val)

    data_list.append(scenario_data_list)

app.line_chart(
    name="National Loss Curve",
    description="Total Annual Average Loss (AAL) [" + project_name + "]",
    x=years,
    y=data_list,
    label=label_list,
    color=color_list,
)

# Debug
debug_text = ""
for d in data_list:
    debug_text = debug_text + str(len(d)) + ", "

debug_text = debug_text + "\r\n" + str(data_list)
#debug_text = ssp_select
#app.display(name="text-2", value=debug_text)
