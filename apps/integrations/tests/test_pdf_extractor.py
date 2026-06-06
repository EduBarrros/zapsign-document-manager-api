from unittest.mock import patch, MagicMock
from apps.integrations.pdf_extractor import PDFExtractor


class TestPDFExtractor:

    @patch("apps.integrations.pdf_extractor.PdfReader")
    @patch("apps.integrations.pdf_extractor.requests.get")
    def test_extract_from_url_returns_combined_text(
        self,
        mock_get,
        mock_pdf_reader,
    ):
        mock_response = MagicMock()
        mock_response.content = b"fake-pdf-content"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        page_1 = MagicMock()
        page_1.extract_text.return_value = "Primeira página"

        page_2 = MagicMock()
        page_2.extract_text.return_value = "Segunda página"

        mock_reader = MagicMock()
        mock_reader.pages = [page_1, page_2]

        mock_pdf_reader.return_value = mock_reader

        result = PDFExtractor.extract_from_url(
            "https://example.com/document.pdf"
        )

        assert result == "Primeira página\nSegunda página"

        mock_get.assert_called_once_with(
            "https://example.com/document.pdf",
            timeout=30
        )

    @patch("apps.integrations.pdf_extractor.PdfReader")
    @patch("apps.integrations.pdf_extractor.requests.get")
    def test_extract_from_url_ignores_empty_pages(
        self,
        mock_get,
        mock_pdf_reader,
    ):
        mock_response = MagicMock()
        mock_response.content = b"fake-pdf-content"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        page_1 = MagicMock()
        page_1.extract_text.return_value = "Texto válido"

        page_2 = MagicMock()
        page_2.extract_text.return_value = None

        page_3 = MagicMock()
        page_3.extract_text.return_value = ""

        mock_reader = MagicMock()
        mock_reader.pages = [page_1, page_2, page_3]

        mock_pdf_reader.return_value = mock_reader

        result = PDFExtractor.extract_from_url(
            "https://example.com/document.pdf"
        )

        assert result == "Texto válido"

    @patch("apps.integrations.pdf_extractor.requests.get")
    def test_extract_from_url_raises_http_error(
        self,
        mock_get,
    ):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception(
            "Download error"
        )

        mock_get.return_value = mock_response

        import pytest

        with pytest.raises(Exception, match="Download error"):
            PDFExtractor.extract_from_url(
                "https://example.com/document.pdf"
            )