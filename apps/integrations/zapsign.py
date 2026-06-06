import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ZapSignClient:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = settings.ZAPSIGN_API_URL

    def create_document(self, name: str, url_pdf: str, signers: list) -> dict:
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

        logger.info(
            'Enviando documento para ZapSign name=%s signers_count=%s',
            name,
            len(signers),
        )

        response = None
        try:
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
        except requests.RequestException:
            logger.error(
                'Falha ao criar documento no ZapSign name=%s status=%s',
                name,
                response.status_code if response is not None else None,
                exc_info=True,
            )
            raise

        result = response.json()
        logger.info(
            'Documento criado no ZapSign name=%s token=%s',
            name,
            result.get('token'),
        )
        return result

    def get_document(self, document_token: str) -> dict:
        logger.info('Consultando documento no ZapSign token=%s', document_token)

        response = None
        try:
            response = requests.get(
                f"{self.base_url}/docs/{document_token}",
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=30
            )
            response.raise_for_status()
        except requests.RequestException:
            logger.error(
                'Falha ao consultar documento no ZapSign token=%s status=%s',
                document_token,
                response.status_code if response is not None else None,
                exc_info=True,
            )
            raise

        return response.json()
