from __future__ import annotations

import re
from collections.abc import Sequence
from typing import TYPE_CHECKING

from .token_chunker import ChunkedText, TokenChunker, _TextUnit

if TYPE_CHECKING:
    from app.infrastructure.pdf.base import ExtractedPage


class SemanticChunker(TokenChunker):
    """Belgenin başlık, paragraf ve madde yapısını dikkate alan chunker."""

    _NUMBERED_HEADING = re.compile(
        r"^(?P<number>(?:\d+\.\d+(?:\.\d+)*)|(?:\d+\.))\s+(?P<title>\S.+)$"
    )
    _ARTICLE_HEADING = re.compile(
        r"^(?:MADDE|ARTICLE)\s+\d+[A-ZÇĞİÖŞÜ]?\s*[-:–]?\s*.*$", re.IGNORECASE
    )
    _LIST_ITEM = re.compile(
        r"^(?:[-•●◦▪]|•|\(?[a-zçğıiöşüA-ZÇĞİÖŞÜ]\)|\d+[.)])\s+"
    )

    def __init__(self) -> None:
        self._active_max_tokens = 900

    def chunk(
        self,
        pages: Sequence[ExtractedPage],
        *,
        document_id: int | None = None,
        min_tokens: int = 500,
        max_tokens: int = 900,
        overlap_tokens: int = 100,
        include_page_markers: bool = True,
    ) -> list[ChunkedText]:
        self._active_max_tokens = max_tokens
        return super().chunk(
            pages,
            document_id=document_id,
            min_tokens=min_tokens,
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens,
            include_page_markers=include_page_markers,
        )

    def _build_units(self, pages: Sequence[ExtractedPage]) -> list[_TextUnit]:
        units: list[_TextUnit] = []
        heading_stack: dict[int, str] = {}
        current_section: str | None = None

        for page in sorted(pages, key=lambda item: item["page_number"]):
            blocks = self._paragraph_blocks(page["text"])
            pending_related: list[str] = []

            def flush_related() -> None:
                if not pending_related:
                    return
                text = "\n".join(pending_related)
                units.extend(
                    self._split_oversized_block(
                        text, page["page_number"], current_section
                    )
                )
                pending_related.clear()

            for block in blocks:
                heading_level = self._heading_level(block)
                if heading_level is not None:
                    flush_related()
                    heading_stack[heading_level] = block
                    heading_stack = {
                        level: title
                        for level, title in heading_stack.items()
                        if level <= heading_level
                    }
                    current_section = " > ".join(
                        heading_stack[level] for level in sorted(heading_stack)
                    )
                    units.append(
                        _TextUnit(
                            block,
                            page["page_number"],
                            current_section,
                            self.count_tokens(block),
                        )
                    )
                    continue

                if self._is_list_item(block):
                    pending_related.append(block)
                    continue

                if pending_related:
                    flush_related()

                # Listeyi tanıtan iki noktalı paragraf sonraki maddelerle birlikte tutulur.
                if block.endswith(":"):
                    pending_related.append(block)
                else:
                    units.extend(
                        self._split_oversized_block(
                            block, page["page_number"], current_section
                        )
                    )

            flush_related()

        return units

    @staticmethod
    def _paragraph_blocks(text: str) -> list[str]:
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
        if len(paragraphs) > 1:
            return paragraphs
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _split_oversized_block(
        self, text: str, page_number: int, section_title: str | None
    ) -> list[_TextUnit]:
        safe_limit = max(1, self._active_max_tokens - 10)
        if self.count_tokens(text) <= safe_limit:
            return [
                _TextUnit(text, page_number, section_title, self.count_tokens(text))
            ]

        pieces = [piece.strip() for piece in text.splitlines() if piece.strip()]
        if len(pieces) == 1:
            pieces = [
                piece.strip()
                for piece in self._SENTENCE_BOUNDARY.split(text)
                if piece.strip()
            ]

        # Büyük bölümlerde alt bloklar overlap aralığıyla uyumlu tutulur.
        # Her alt blok yine yalnızca tam cümle veya tam madde sınırında biter.
        split_limit = min(150, safe_limit)
        units: list[_TextUnit] = []
        current: list[str] = []
        current_tokens = 0

        for piece in pieces:
            piece_tokens = self.count_tokens(piece)
            if current and current_tokens + piece_tokens > split_limit:
                joined = "\n".join(current)
                units.append(
                    _TextUnit(joined, page_number, section_title, current_tokens)
                )
                current = []
                current_tokens = 0
            current.append(piece)
            current_tokens += piece_tokens

        if current:
            joined = "\n".join(current)
            units.append(_TextUnit(joined, page_number, section_title, current_tokens))

        return units

    def _heading_level(self, text: str) -> int | None:
        line = text.strip()
        if len(line) > 160 or "\n" in line:
            return None
        if self._ARTICLE_HEADING.match(line):
            return 1
        match = self._NUMBERED_HEADING.match(line)
        if match:
            number = match.group("number").rstrip(".")
            return number.count(".") + 1
        if line.startswith("#"):
            return min(len(line) - len(line.lstrip("#")), 6)
        letters = [character for character in line if character.isalpha()]
        if letters and len(letters) >= 3 and all(character.isupper() for character in letters):
            return 1
        return None

    def _is_list_item(self, text: str) -> bool:
        return bool(self._LIST_ITEM.match(text.strip()))
