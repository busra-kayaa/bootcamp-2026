from app.infrastructure.chunking.token_chunker import ChunkedText, TokenChunker
from app.infrastructure.pdf.pdfplumber_extractor import PdfPlumberExtractor
from app.infrastructure.pdf.text_combiner import TextCombiner


class DocumentIngestionPipeline:
    """
    PDF'den sayfa bazlı metin çıkarır, temizler, birleştirir ve chunk'lara böler.
    """

    def __init__(
        self,
        extractor: PdfPlumberExtractor | None = None,
        combiner: TextCombiner | None = None,
        chunker: TokenChunker | None = None,
    ) -> None:
        self._extractor = extractor or PdfPlumberExtractor()
        self._combiner = combiner or TextCombiner()
        self._chunker = chunker or TokenChunker()

    def process(
        self,
        file_path: str,
        *,
        max_chars: int = 4000,
    ) -> dict[str, object]:
        pages = self._extractor.extract(file_path)
        combined_text = self._combiner.combine(pages)
        chunks: list[ChunkedText] = self._chunker.chunk(
            pages,
            max_chars=max_chars,
        )

        return {
            "pages": pages,
            "combined_text": combined_text,
            "chunks": chunks,
        }
