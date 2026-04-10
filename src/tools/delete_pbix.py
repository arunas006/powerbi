from __future__ import annotations
from src.config import get_settings
import requests
from src.tools.auth import get_auth_headers
from src.tools.workspace import get_workspace_id
from src.tools.export_pbix import report_details
import os

settings = get_settings()

def delete_report(workspace_id, report_id, headers):

    """Deletes a Power BI report."""

    url = f"{settings.POWER_BI_BASE_URL}/groups/{workspace_id}/reports/{report_id}"

    headers.pop("Content-Type", None)
    
    res = requests.delete(url, headers=headers)
       
    if res.status_code == 404:
        raise Exception(f"Report {report_id} not found")

def delete_dataset(workspace_id, dataset_id, headers):

    """Deletes a Power BI dataset."""
    url = f"{settings.POWER_BI_BASE_URL}/groups/{workspace_id}/datasets/{dataset_id}"

    headers.pop("Content-Type", None)
    
    res = requests.delete(url, headers=headers)

    if res.status_code == 404:
        raise Exception(f"Dataset {dataset_id} not found")

if __name__ == "__main__":
    headers = get_auth_headers()
    workspace_id = get_workspace_id("Prod", headers)

    data = report_details("invoice-Dashboard", "Prod")
  
    delete_report(workspace_id, data['report_id'], headers)
    delete_dataset(workspace_id, data['dataset_id'], headers)