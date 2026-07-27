from collections.abc import Sequence
from typing import TypedDict

from app.infrastructure.pdf.base import ExtractedPage


class ChunkedText(TypedDict):
    chunk_index: int
    text: str
    page_start: int
    page_end: int
    page_numbers: list[int]
    extraction_methods: list[str]
    character_count: int


class TokenChunker:
    """
    Sayfa sırasını koruyarak metni anlamlı parçalara böler.

    Boş sayfalar atılır. Chunk içinde sayfa sınırları marker ile korunur.
    """

    def chunk(
        self,
        pages: Sequence[ExtractedPage],
        *,
        max_chars: int = 4000,
        include_page_markers: bool = True,
    ) -> list[ChunkedText]:
        ordered_pages = sorted(pages, key=lambda page: page["page_number"])
        chunks: list[ChunkedText] = []

        current_parts: list[str] = []
        current_pages: list[int] = []
        current_methods: list[str] = []
        current_length = 0

        def flush() -> None:
            nonlocal current_parts, current_pages, current_methods, current_length

            if not current_parts:
                return

            chunks.append(
                {
                    "chunk_index": len(chunks) + 1,
                    "text": "\n\n".join(current_parts).strip(),
                    "page_start": current_pages[0],
                    "page_end": current_pages[-1],
                    "page_numbers": list(current_pages),
                    "extraction_methods": list(current_methods),
                    "character_count": current_length,
                }
            )

            current_parts = []
            current_pages = []
            current_methods = []
            current_length = 0

        for page in ordered_pages:
            page_text = page["text"].strip()

            if not page_text:
                continue

            page_marker = self._build_page_marker(page)
            page_block = (
                f"{page_marker}\n{page_text}" if include_page_markers else page_text
            )

            if current_parts and current_length + len(page_block) > max_chars:
                flush()

            if len(page_block) <= max_chars:
                current_parts.append(page_block)
                current_pages.append(page["page_number"])
                current_methods.append(page["extraction_method"])
                current_length += len(page_block)
                continue

            if current_parts:
                flush()

            for split_block in self._split_long_block(page_block, max_chars):
                chunks.append(
                    {
                        "chunk_index": len(chunks) + 1,
                        "text": split_block,
                        "page_start": page["page_number"],
                        "page_end": page["page_number"],
                        "page_numbers": [page["page_number"]],
                        "extraction_methods": [page["extraction_method"]],
                        "character_count": len(split_block),
                    }
                )

        flush()
        return chunks

    @staticmethod
    def _build_page_marker(page: ExtractedPage) -> str:
        return f"[Sayfa {page['page_number']} | {page['extraction_method']}]"

    @staticmethod
    def _split_long_block(block: str, max_chars: int) -> list[str]:
        if len(block) <= max_chars:
            return [block.strip()]

        lines = block.splitlines()
        marker = lines[0].strip() if lines else ""
        body = "\n".join(lines[1:]).strip()
        words = body.split()
        parts: list[str] = []

        current_words: list[str] = []
        current_length = len(marker) + 1 if marker else 0

        for word in words:
            additional_length = len(word) + (1 if current_words else 0)

            if current_words and current_length + additional_length > max_chars:
                part_body = " ".join(current_words).strip()
                parts.append(f"{marker}\n{part_body}".strip() if marker else part_body)
                current_words = []
                current_length = len(marker) + 1 if marker else 0

            current_words.append(word)
            current_length += additional_length

        if current_words:
            part_body = " ".join(current_words).strip()
            parts.append(f"{marker}\n{part_body}".strip() if marker else part_body)

        return [part for part in parts if part]
