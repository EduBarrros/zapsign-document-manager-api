from io import BytesIO

import requests
from pypdf import PdfReader


class PDFExtractor:

    @staticmethod
    def extract_from_url(pdf_url: str) -> str:
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

        return "\n".join(pages_content)