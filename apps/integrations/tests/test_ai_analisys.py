from unittest.mock import patch, MagicMock
from apps.integrations.ai_analysis import GeminiClient


class TestAiAnalaisysClient:

    @patch('apps.integrations.ai_analysis.genai.Client')
    def test_analyze_document_success_with_clean_json(self, mock_client_class, settings):
        settings.GEMINI_KEY = "fake-key"

        mock_response = MagicMock()
        mock_response.text = '{"summary": "Contrato OK", "missing_topics": [], "insights": "Sem riscos"}'

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = GeminiClient()
        result = client.analyze_document("Texto do contrato")

        assert result["summary"] == "Contrato OK"
        assert result["insights"] == "Sem riscos"
        assert result["missing_topics"] == []

    @patch('apps.integrations.ai_analysis.genai.Client')
    def test_analyze_document_failure_returns_fallback_dictionary(self, mock_client_class, settings):
        settings.GEMINI_KEY = "fake-key"

        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client

        client = GeminiClient()
        result = client.analyze_document("Texto do contrato")

        assert result["summary"] == "Analysis unavailable"
        assert result["insights"] == "Analysis unavailable"
        assert result["missing_topics"] == []
