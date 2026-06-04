import requests
from django.conf import settings


class ZapSignClient:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = settings.ZAPSIGN_API_URL

    def create_document(self, name: str, url_pdf:str, signers: list) -> dict:
        payload = {
            "name": name,
            "url_pdf": url_pdf,
            "signers": [
                {
                    "name": signer['name'],
                    "email": signer['email'],
                }
                for signer in signers
            ]
        }

        response = requests.post(
            f"{self.base_url}/docs/",
            json=payload,
            headers={
                "Authorization": f"Bearer {self.api_token}", 
                "Content-Type": "application/json"
            },
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    def get_document(self, document_token: str) -> dict:
        response = requests.get(
            f"{self.base_url}/docs/{document_token}",
            headers={"Authorization": f"Bearer {self.api_token}"},
            timeout=30
        )

        response.raise_for_status()
        return response.json()