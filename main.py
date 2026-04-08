import requests
from dotenv import load_dotenv
import os
load_dotenv()

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

data = {
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": "https://analysis.windows.net/powerbi/api/.default",
    "grant_type": "client_credentials"
}

res = requests.post(url, data=data)
token = res.json().get("access_token")
# print(token)

headers = {
    "Authorization": f"Bearer {token}"
}

url = "https://api.powerbi.com/v1.0/myorg/groups"

res = requests.get(url, headers=headers)

workspaces = res.json()["value"]


DEV_WORKSPACE_NAME = os.getenv("DEV_WORKSPACE") 

def get_workspace_id(name, headers):
    url = "https://api.powerbi.com/v1.0/myorg/groups"
    res = requests.get(url, headers=headers)
    
    for ws in res.json()["value"]:
        if ws["name"] == name:
            return ws["id"]
    
    return None

def get_report_id(workspace_id, report_name, headers):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports"
    res = requests.get(url, headers=headers)

    for rpt in res.json()["value"]:
        if rpt["name"] == report_name:
            return rpt["id"], rpt["datasetId"]

    return None,None

dev_workspace_id = get_workspace_id("Dev", headers)

report_id, dataset_id = get_report_id(dev_workspace_id, "Sales-Dashboard", headers)

print("Report ID:", report_id)
print("Dataset ID:", dataset_id)


prod_workspace_id = get_workspace_id("Prod", headers)

prod_workspace_id = get_workspace_id("Prod", headers)
print("Prod Workspace ID:", prod_workspace_id)



def export_pbix(workspace_id, report_id, headers, file_path):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/Export"

    res = requests.get(url, headers=headers, stream=True)

    if res.status_code != 200:
        print("Export failed:", res.text)
        return None

    with open(file_path, "wb") as f:
        for chunk in res.iter_content(chunk_size=1024):
            f.write(chunk)

    print("Export completed:", file_path)
    return file_path

def upload_pbix(workspace_id, file_path, headers):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?datasetDisplayName=Sales-Dataset&nameConflict=CreateOrOverwrite"

    with open(file_path, "rb") as f:
        files = {
            'file': (file_path, f, 'application/octet-stream')
        }

        res = requests.post(url, headers=headers, files=files)

    if res.status_code not in [200, 202]:
        print("Upload failed:", res.text)
        return None

    response = res.json()
    import_id = response["id"]

    print("Import ID:", import_id)
    return import_id
import time

def check_import_status(workspace_id, import_id, headers):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports/{import_id}"

    while True:
        res = requests.get(url, headers=headers)
        data = res.json()

        status = data["importState"]
        print("Status:", status)

        if status == "Succeeded":
            dataset_id = data["datasets"][0]["id"]
            report_id = data["reports"][0]["id"]

            return dataset_id, report_id

        elif status == "Failed":
            print("Import failed:", data)
            return None, None

        time.sleep(5)

file_path = export_pbix(dev_workspace_id, report_id, headers, "exported.pbix")

# Step 2: Upload
import_id = upload_pbix(prod_workspace_id, file_path, headers)

# Step 3: Wait + get dataset/report
dataset_id, new_report_id = check_import_status(prod_workspace_id, import_id, headers)

print("Dataset ID:", dataset_id)
print("Report ID:", new_report_id)
# url = "https://api.powerbi.com/v1.0/myorg/gateways"
# res = requests.get(url, headers=headers)

# print(res.json())



