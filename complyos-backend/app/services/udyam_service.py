import httpx
from typing import Optional, Dict

class UdyamService:
    @staticmethod
    async def verify_udyam(udyam_number: str) -> Optional[Dict]:
        """
        Mock call to Udyam API. 
        In production, this would use httpx to call govt/third-party API.
        """
        # Mocking a successful response for valid-looking format
        if udyam_number.startswith("UDYAM-"):
            return {
                "business_name": "Mock MSME Enterprises",
                "category": "Small",
                "state": "Maharashtra",
                "district": "Mumbai",
                "nic_code": "6201"
            }
        return None

    @staticmethod
    async def get_udyam_details(udyam_number: str) -> Optional[Dict]:
        """Wrapper to fetch and format details"""
        details = await UdyamService.verify_udyam(udyam_number)
        return details
