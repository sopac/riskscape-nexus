# Riskscape Nexus Integration

Utility scripts designed to run as automated scheduled tasks that performs the following - 

1. Download and store a project model run outputs most recent outputs via the Riskscape Platform API
2. Upload and register that regional-summary, national-loss-curves, buildings-impact and admin-regional-impact spatial outputs
3. Generate a PDF with SLR and Annual Avergae Loss and Upload to Nexus Documents
4. Generate/update a Dashboard by injecting template in GeoApps base resource table 

#### Usage

Create a Python Virtual Environment (using virtualenvwrapper etc.)

Install dependencies
`pip install -U -r requirements.txt`

Copy `env.sample` to `.env` and and populate credentials.

List Riskscape Projects and Group Available to the User:
`python riskscape_list_projects.py`

Run integration using `python riskscape_integration.py project-name` eg: cook-islands, tonga etc (from above listing)







