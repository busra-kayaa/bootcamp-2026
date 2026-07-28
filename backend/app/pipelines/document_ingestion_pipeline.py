import asyncio
from pathlib import Path

from app.infrastructure.chunking.semantic_chunker import SemanticChunker
from app.infrastructure.chunking.token_chunker import ChunkedText, TokenChunker
from app.infrastructure.pdf.docx_extractor import DocxExtractor
from app.infrastructure.pdf.pdfplumber_extractor import PdfPlumberExtractor
from app.infrastructure.preprocessing.header_footer_cleaner import HeaderFooterCleaner
from app.infrastructure.preprocessing.text_preprocessor import TextPreprocessor


class DocumentIngestionPipeline:
    """
    Belgeyi doğrular, metni çıkarıp temizler ve anlamsal chunk'lara böler.
    """

    def __init__(
        self,
        pdf_extractor: PdfPlumberExtractor | None = None,
        docx_extractor: DocxExtractor | None = None,
        chunker: TokenChunker | None = None,
        text_preprocessor: TextPreprocessor | None = None,
        header_footer_cleaner: HeaderFooterCleaner | None = None,
    ) -> None:
        self._pdf_extractor = pdf_extractor or PdfPlumberExtractor()
        self._docx_extractor = docx_extractor or DocxExtractor()
        self._chunker = chunker or SemanticChunker()
        self._text_preprocessor = text_preprocessor or TextPreprocessor()
        self._header_footer_cleaner = header_footer_cleaner or HeaderFooterCleaner()

    async def process(
        self,
        document_id: int,
        file_path: str,
        *,
        min_tokens: int = 500,
        max_tokens: int = 900,
        overlap_tokens: int = 100,
    ) -> dict[str, object]:
        if document_id < 1:
            raise ValueError("document_id pozitif bir tam sayı olmalıdır.")

        path = Path(file_path)
        self._validate_file(path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            pages = await asyncio.to_thread(self._pdf_extractor.extract, path)
        elif suffix == ".docx":
            pages = await asyncio.to_thread(self._docx_extractor.extract, path)
        else:
            raise ValueError(
                "Desteklenmeyen dosya türü. Yalnızca PDF ve DOCX kabul edilir."
            )

        pages = self._header_footer_cleaner.clean(pages)
        pages = [
            {**page, "text": self._text_preprocessor.clean(page["text"])}
            for page in pages
        ]

        if not any(page["text"].strip() for page in pages):
            raise ValueError("Belgede temizleme sonrası okunabilir metin bulunamadı.")

        chunks: list[ChunkedText] = self._chunker.chunk(
            pages,
            document_id=document_id,
            min_tokens=min_tokens,
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens,
        )

        methods = {
            page["extraction_method"]
            for page in pages
            if page["text"].strip()
        }
        extraction_method = next(iter(methods)) if len(methods) == 1 else "hybrid"

        return {
            "document_id": document_id,
            "page_count": len(pages),
            "character_count": sum(len(page["text"]) for page in pages),
            "extraction_method": extraction_method,
            "chunks": chunks,
        }

    @staticmethod
    def _validate_file(path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {path}")
        if not path.is_file():
            raise ValueError(f"Verilen yol bir dosyaya ait değil: {path}")
        if path.stat().st_size == 0:
            raise ValueError("Dosya boş.")
