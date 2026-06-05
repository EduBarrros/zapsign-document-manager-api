from unittest.mock import patch, MagicMock
import pytest
from apps.integrations.zapsign import ZapSignClient


class TestZapSignClient:

    @patch("apps.integrations.zapsign.requests.post")
    def test_create_document_returns_response_json(
        self,
        mock_post,
        settings,
    ):
        settings.ZAPSIGN_API_URL = "https://api.zapsign.com.br"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "token": "doc-token"
        }
        mock_response.raise_for_status.return_value = None

        mock_post.return_value = mock_response

        client = ZapSignClient(api_token="fake-token")

        result = client.create_document(
            name="Contrato",
            url_pdf="https://example.com/contrato.pdf",
            signers=[
                {
                    "name": "João",
                    "email": "joao@email.com",
                }
            ],
        )

        assert result == {
            "token": "doc-token"
        }

        mock_post.assert_called_once_with(
            "https://api.zapsign.com.br/docs/",
            json={
                "name": "Contrato",
                "url_pdf": "https://example.com/contrato.pdf",
                "signers": [
                    {
                        "name": "João",
                        "email": "joao@email.com",
                    }
                ],
            },
            headers={
                "Authorization": "Bearer fake-token",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

    @patch("apps.integrations.zapsign.requests.post")
    def test_create_document_raises_http_error(
        self,
        mock_post,
        settings,
    ):
        settings.ZAPSIGN_API_URL = "https://api.zapsign.com.br"

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception(
            "ZapSign error"
        )

        mock_post.return_value = mock_response

        client = ZapSignClient(api_token="fake-token")

        with pytest.raises(Exception, match="ZapSign error"):
            client.create_document(
                name="Contrato",
                url_pdf="https://example.com/contrato.pdf",
                signers=[],
            )

    @patch("apps.integrations.zapsign.requests.get")
    def test_get_document_returns_response_json(
        self,
        mock_get,
        settings,
    ):
        settings.ZAPSIGN_API_URL = "https://api.zapsign.com.br"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "token": "doc-token",
            "status": "signed",
        }
        mock_response.raise_for_status.return_value = None

        mock_get.return_value = mock_response

        client = ZapSignClient(api_token="fake-token")

        result = client.get_document("doc-token")

        assert result == {
            "token": "doc-token",
            "status": "signed",
        }

        mock_get.assert_called_once_with(
            "https://api.zapsign.com.br/docs/doc-token",
            headers={
                "Authorization": "Bearer fake-token"
            },
            timeout=30,
        )

    @patch("apps.integrations.zapsign.requests.get")
    def test_get_document_raises_http_error(
        self,
        mock_get,
        settings,
    ):
        settings.ZAPSIGN_API_URL = "https://api.zapsign.com.br"

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception(
            "ZapSign error"
        )

        mock_get.return_value = mock_response

        client = ZapSignClient(api_token="fake-token")

        with pytest.raises(Exception, match="ZapSign error"):
            client.get_document("doc-token")