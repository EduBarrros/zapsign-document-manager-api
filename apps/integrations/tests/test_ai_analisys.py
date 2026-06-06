# apps/documents/tests/test_gemini_client.py
from unittest.mock import patch, MagicMock
from apps.integrations.ai_analysis import GeminiClient


class TestAiAnalaisysClient:

    @patch('apps.integrations.ai_analysis.genai.GenerativeModel')
    @patch('apps.integrations.ai_analysis.genai.configure')
    def test_analyze_document_success_with_clean_json(self, mock_configure, mock_model_class, settings):
        settings.GEMINI_KEY = "fake-key"
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value.text = '{"summary": "Contrato OK", "missing_topics": [], "insights": "Sem riscos"}'
        mock_model_class.return_value = mock_model

        client = GeminiClient()
        result = client.analyze_document("Texto do contrato")

        assert result["summary"] == "Contrato OK"
        assert result["insights"] == "Sem riscos"
        assert result["missing_topics"] == []

    @patch('apps.integrations.ai_analysis.genai.GenerativeModel')
    @patch('apps.integrations.ai_analysis.genai.configure') 
    def test_analyze_document_failure_returns_fallback_dictionary(self, mock_configure, mock_model_class, settings):
        settings.GEMINI_KEY = "fake-key"
        
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model

        client = GeminiClient()
        result = client.analyze_document("Texto do contrato")

        assert result["summary"] == "Analysis unavailable"
        assert result["insights"] == "Analysis unavailable"
        assert result["missing_topics"] == []