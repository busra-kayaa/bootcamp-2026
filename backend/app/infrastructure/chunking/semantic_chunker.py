from collections.abc import Sequence

from app.infrastructure.pdf.base import ExtractedPage

from .token_chunker import ChunkedText, TokenChunker


class SemanticChunker:
    """
    Şimdilik token tabanlı chunking üzerine oturan daha üst seviye ayraç.

    İleride anlamsal bölme eklendiğinde bu sınıf genişletilebilir.
    """

    def __init__(self, token_chunker: TokenChunker | None = None) -> None:
        self._token_chunker = token_chunker or TokenChunker()

    def chunk(
        self,
        pages: Sequence[ExtractedPage],
        *,
        max_chars: int = 4000,
        include_page_markers: bool = True,
    ) -> list[ChunkedText]:
        return self._token_chunker.chunk(
            pages,
            max_chars=max_chars,
            include_page_markers=include_page_markers,
        )
