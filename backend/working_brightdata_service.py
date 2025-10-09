
import requests
import json
from typing import Dict, List, Optional

class WorkingBrightDataService:
    """
    Working BrightData service based on API discovery
    """
    
    def __init__(self):
        self.token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
        self.base_url = "https://api.brightdata.com"  # Confirmed working
        self.dataset_instagram = "gd_lk5ns7kz21pck8jpis"
        self.dataset_facebook = "gd_lkaxegm826bjpoo9m5"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def list_datasets(self) -> Dict:
        """List available datasets (confirmed working)"""
        url = f"{self.base_url}/datasets/list"
        response = requests.get(url, headers=self.headers)
        return {"status_code": response.status_code, "data": response.json() if response.status_code == 200 else response.text}
    
    def trigger_scraping(self, dataset_id: str, search_term: str) -> Dict:
        """Trigger scraping job (pattern to be confirmed)"""
        # Test multiple patterns based on discovery
        trigger_patterns = [
            (f"{self.base_url}/datasets/{dataset_id}/trigger", {"url": search_term}),
            (f"{self.base_url}/v1/datasets/{dataset_id}/trigger", {"search_term": search_term}),
            (f"{self.base_url}/collect/{dataset_id}/trigger", {"query": search_term}),
        ]
        
        for url, payload in trigger_patterns:
            try:
                response = requests.post(url, headers=self.headers, json=payload)
                if response.status_code == 200:
                    return {"status": "success", "url": url, "payload": payload, "data": response.json()}
            except Exception as e:
                continue
                
        return {"status": "error", "message": "No working trigger pattern found"}
    
    def get_snapshots(self, dataset_id: str) -> Dict:
        """Get snapshots for dataset"""
        # Test multiple snapshot patterns
        snapshot_patterns = [
            f"{self.base_url}/datasets/{dataset_id}/snapshots",
            f"{self.base_url}/v1/datasets/{dataset_id}/snapshots", 
            f"{self.base_url}/datasets/{dataset_id}",
        ]
        
        for url in snapshot_patterns:
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    return {"status": "success", "url": url, "data": response.json()}
            except Exception as e:
                continue
                
        return {"status": "error", "message": "No working snapshot pattern found"}
