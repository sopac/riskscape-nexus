import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
organisation = "partner-2"

RISKSCAPE_API = os.getenv("RISKSCAPE_API")
RISKSCAPE_USERNAME = os.getenv("RISKSCAPE_USERNAME")
RISKSCAPE_PASSWORD = os.getenv("RISKSCAPE_PASSWORD")
GEONODE_API = os.getenv("GEONODE_API")
GEONODE_USERNAME = os.getenv("GEONODE_USERNAME")
GEONODE_PASSWORD = os.getenv("GEONODE_PASSWORD")
api_url = RISKSCAPE_API

# authenication token
token_url = f"{api_url}/token"
auth = {"usernameOrEmail": "sachindras", "password": "Daemon21!@"}
response = requests.post(token_url, json=auth)
token = response.text

# project information
url = f"{api_url}/users/by-username/{RISKSCAPE_USERNAME}/projects/all"
response = requests.get(url, headers={"rs-api-token": token})
project_text = response.text
# print(project_text)
projects = json.loads(project_text)
print("id\tgroup\t\tname")
print("--\t-----\t\t----")
for p in projects["list"]:
    # print(p)
    id = p["id"]
    group = p["groupSlug"]
    name = p["slug"]

    print(str(id) + "\t" + group + " \t" + name)
