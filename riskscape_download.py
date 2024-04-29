import requests
import json
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore') 

load_dotenv()
#project_name = "cook-islands"
project_name = "rsmc-tcwc"

organisation = "partner"
api_url = "https://riskscape.nz/api"

RISKSCAPE_API = os.getenv('RISKSCAPE_API')
RISKSCAPE_USERNAME = os.getenv('RISKSCAPE_USERNAME')
RISKSCAPE_PASSWORD = os.getenv('RISKSCAPE_PASSWORD')
GEONODE_API = os.getenv('GEONODE_API')
GEONODE_USERNAME = os.getenv('GEONODE_USERNAME')
GEONODE_PASSWORD = os.getenv('GEONODE_PASSWORD')

# authenication token
token_url = f"{api_url}/token"
auth = {"usernameOrEmail": "sachindras", "password": "Daemon21!@"}
response = requests.post(token_url, json=auth, verify=False)
token = response.text
# print(token)

#list projects
#https://riskscape.nz/api/users/by-username/sachindras/projects/all

# project information
url = f"{api_url}/projects/by-slug/{organisation}/{project_name}"
response = requests.get(url, headers={"rs-api-token": token}, verify=False)
project_text = response.text
#print(project_text)
project = json.loads(project_text)
print(project)
id = project["id"]

# recent runs
url = f"{api_url}/projects/by-id/{str(id)}/runs/recent"
response = requests.get(url, headers={"rs-api-token": token}, verify=False)
model_run_text = response.text
model_run = json.loads(model_run_text)
# print(model_run)
model_name = model_run["list"][0]["externalModelId"]
print(model_name)

#create data directories
data_dir_path = "data/" + project_name
if not os.path.exists(data_dir_path):
    os.makedirs(data_dir_path)

#download spatial model outputs
for output in model_run["list"][0]["outputs"]:
    if output["mediaType"] == "application/geo+json":
        print(output)
        output_name = output["name"]
        output_url = api_url + output["uri"].replace("/api", "") + "/download"
        print(output_url)
        # download
        file_name = (
            #project_name
            #+ "_" +
            model_name.lower()
            + "_"
            + output_name.lower()
            + ".geojson"
        )
        file_name = file_name.replace("_", "-")
        print(file_name)
        response = requests.get(output_url, headers={"rs-api-token": token}, verify=False)
        # print(response.text)
        with open("data/" + project_name + "/" + file_name, mode="wb") as file:
            file.write(response.content)

#download tabular model outputs
for output in model_run["list"][0]["outputs"]:
    if output["mediaType"] == "text/csv":
        print(output)
        output_name = output["name"]
        output_url = api_url + output["uri"].replace("/api", "") + "/download"
        print(output_url)
        # download
        file_name = (
            #project_name
            #+ "_" +
            model_name.lower()
            + "_"
            + output_name.lower()
            + ".csv"
        )
        file_name = file_name.replace("_", "-")
        print(file_name)
        response = requests.get(output_url, headers={"rs-api-token": token}, verify=False)
        # print(response.text)
        with open("data/" + project_name + "/" + file_name, mode="wb") as file:
            file.write(response.content)
