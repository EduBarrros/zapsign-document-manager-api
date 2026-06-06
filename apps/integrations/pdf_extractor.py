import logging
from io import BytesIO

import requests
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class PDFExtractor:

    @staticmethod
    def extract_from_url(pdf_url: str) -> str:
        logger.info('Extraindo texto do PDF url=%s', pdf_url)

        try:
            response = requests.get(
                pdf_url,
                timeout=30
            )
            response.raise_for_status()

            pdf_file = BytesIO(response.content)
            reader = PdfReader(pdf_file)

            pages_content = []

            for page in reader.pages:
                text = page.extract_text()

                if text:
                    pages_content.append(text)

            content = "\n".join(pages_content)
            logger.info(
                'Texto extraído do PDF url=%s pages=%s content_length=%s',
                pdf_url,
                len(reader.pages),
                len(content),
            )
            return content

        except Exception:
            logger.error(
                'Falha ao extrair texto do PDF url=%s',
                pdf_url,
                exc_info=True,
            )
            raise
