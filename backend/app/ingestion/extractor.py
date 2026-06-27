import io
from pathlib import Path
from loguru import logger

import PyPDF2
import docx
import pandas as pd
from PIL import Image
import pytesseract


class TextExtractor:

    async def extract(self, file_path: str, file_type: str) -> dict:
        """Extract text and metadata from a document."""
        path = Path(file_path)
        if not path.exists():
            return {"text": "", "page_count": 0, "word_count": 0, "error": "File not found"}

        try:
            if file_type == "pdf":
                return await self._extract_pdf(file_path)
            elif file_type == "docx":
                return await self._extract_docx(file_path)
            elif file_type == "txt" or file_type == "md":
                return await self._extract_txt(file_path)
            elif file_type == "csv":
                return await self._extract_csv(file_path)
            elif file_type == "xlsx":
                return await self._extract_xlsx(file_path)
            elif file_type in ("png", "jpg", "jpeg"):
                return await self._extract_image(file_path)
            else:
                return {"text": "", "page_count": 0, "word_count": 0, "error": f"Unsupported type: {file_type}"}
        except Exception as e:
            logger.error(f"Extraction error for {file_path}: {e}")
            return {"text": "", "page_count": 0, "word_count": 0, "error": str(e)}

    async def _extract_pdf(self, path: str) -> dict:
        text_parts = []
        page_count = 0
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            page_count = len(reader.pages)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t.strip())
        text = "\n\n".join(text_parts)
        return {
            "text": text,
            "page_count": page_count,
            "word_count": len(text.split()),
        }

    async def _extract_docx(self, path: str) -> dict:
        doc = docx.Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n\n".join(paragraphs)
        return {
            "text": text,
            "page_count": 1,
            "word_count": len(text.split()),
        }

    async def _extract_txt(self, path: str) -> dict:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return {
            "text": text,
            "page_count": 1,
            "word_count": len(text.split()),
        }

    async def _extract_csv(self, path: str) -> dict:
        df = pd.read_csv(path)
        text = df.to_string(index=False)
        return {
            "text": text,
            "page_count": 1,
            "word_count": len(text.split()),
        }

    async def _extract_xlsx(self, path: str) -> dict:
        df = pd.read_excel(path, sheet_name=None)
        parts = []
        for sheet_name, sheet_df in df.items():
            parts.append(f"Sheet: {sheet_name}\n{sheet_df.to_string(index=False)}")
        text = "\n\n".join(parts)
        return {
            "text": text,
            "page_count": len(df),
            "word_count": len(text.split()),
        }

    async def _extract_image(self, path: str) -> dict:
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        return {
            "text": text,
            "page_count": 1,
            "word_count": len(text.split()),
        }