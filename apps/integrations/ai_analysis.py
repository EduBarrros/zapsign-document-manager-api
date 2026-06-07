import json
import logging

from google import genai
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_KEY)

    def analyze_document(self, document_content: str) -> dict:
        prompt = f"""
        Você é um analista especializado em documentos e contratos.

        Analise o conteúdo abaixo e retorne:

        1. Resumo executivo
        2. Tópicos importantes ausentes
        3. Possíveis riscos
        4. Insights relevantes

        Documento:

        {document_content}

        Retorne APENAS JSON:
        {{
            "summary": "...",
            "missing_topics": [],
            "insights": "..."
        }}
        """

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            text = response.text.strip()

            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]

            result = json.loads(text)
            logger.info(
                'Análise Gemini concluída content_length=%s',
                len(document_content),
            )
            return result

        except Exception:
            logger.warning(
                'Falha na análise Gemini content_length=%s',
                len(document_content),
                exc_info=True,
            )
            return {
                "summary": "Analysis unavailable",
                "missing_topics": [],
                "insights": "Analysis unavailable"
            }
