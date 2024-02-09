import requests
import json
from requests.auth import HTTPBasicAuth

file_name = "cook-islands-coastal-slr-risk-regional-summary.json"
sld_name = file_name.replace(".json", ".sld")

geonode_url = "https://geonode.pacificdata.org"
basic = HTTPBasicAuth("admin", "nexus2024")

# Upload and Create Layer
upload_url = geonode_url + "/api/v2/uploads/upload"

payload = {"title": "PARTNer 2 - Cook Islands"}

files = [
    ("json_file", (file_name, open(file_name, "rb"), "application/geo+json")),
    ("sld_file", (file_name, open(sld_name, "rb"), "application/geo+json")),
]

# application/octet-stream
# application/geo+json

response = requests.request(
    "POST", upload_url, auth=basic, files=files
)  # , data=payload)
print(response.content)


# Create Map
# POST /api/v2/maps/

# Generate Dashboard
# https://geonode.pacificdata.org/en-us/admin/geoapps/geoapp/11/change/
# select resourcebase_ptr_id from geoapps_geoapp;
# Blob field from : select blob from base_resourcebase where id=11;
