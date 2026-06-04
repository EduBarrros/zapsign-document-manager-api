import google.generativeai as genai
from django.conf import settings
import json

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

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
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
           
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]

            return json.loads(text)
        
        except Exception as exception:
            return{
                "summary": "Analysis unavailable",
                "missing_topics": [],
                "insights": "Analysis unavailable"
            }
