import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class WebhookDispatcher:
    def dispatch(self, event: str, payload: dict) -> None:
        url = getattr(settings, 'N8N_WEBHOOK_URL', None)
        if not url:
            return

        body = {'event': event, **payload}
        try:
            requests.post(url, json=body, timeout=5)
            logger.info('Webhook despachado event=%s url=%s', event, url)
        except Exception:
            logger.warning('Falha ao despachar webhook event=%s', event, exc_info=True)
