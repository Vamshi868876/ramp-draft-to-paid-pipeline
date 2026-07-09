import requests
import base64

from config import (
    CLIENT_ID,
    CLIENT_SECRET,
    BASE_URL
)


class RampAPI:


    def __init__(self):
        self.token = None


    def authenticate(self):

        auth = f"{CLIENT_ID}:{CLIENT_SECRET}"

        encoded = base64.b64encode(
            auth.encode()
        ).decode()


        response = requests.post(
            f"{BASE_URL}/developer/v1/token",
            headers={
                "Authorization":
                f"Basic {encoded}",
                "Content-Type":
                "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "client_credentials",
                "scope": "bills:read bills:write entities:read vendors:read"
            }
        )


        response.raise_for_status()

        self.token = response.json()["access_token"]

        return self.token



    def headers(self):

        if not self.token:
            self.authenticate()


        return {
            "Authorization":
            f"Bearer {self.token}",
            "Content-Type":
            "application/json"
        }



    def get_draft_bills(self):

        # We will fetch all bills and filter for Drafts inside Python
        all_bills = []
        url = f"{BASE_URL}/developer/v1/bills/drafts?page_size=100"
        
        while url:
            response = requests.get(url, headers=self.headers())
            
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(f"API Error fetching bills: {response.text}")
                raise e
                
            data = response.json()
            all_bills.extend(data.get("data", []))
            
            # Follow pagination to get all pages
            url = data.get("page", {}).get("next")
            
        # Return a structure that mimics the original single-page response for compatibility
        return {"data": all_bills}

    def delete_bill(self, bill_id):
        
        response = requests.delete(
            f"{BASE_URL}/developer/v1/bills/{bill_id}",
            headers=self.headers()
        )

        # Ramp returns 204 No Content for successful deletion
        response.raise_for_status()
        return True



    def create_and_pay_bill(self, bill_payload):

        response = requests.post(
            f"{BASE_URL}/developer/v1/bills",
            headers=self.headers(),
            json=bill_payload
        )


        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise e

        return response.json()
