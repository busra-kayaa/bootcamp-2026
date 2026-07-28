from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from app.infrastructure.pdf.base import ExtractedPage


class ChunkedText(TypedDict):
    chunk_id: str
    document_id: int | None
    text: str
    page_start: int
    page_end: int
    chunk_index: int
    token_count: int
    section_title: str | None


@dataclass(frozen=True)
class _TextUnit:
    text: str
    page_number: int
    section_title: str | None
    token_count: int


class TokenChunker:
    """Metni cümle sınırlarını ve sayfa bilgisini koruyarak böler."""

    _TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]", re.UNICODE)
    _SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")

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
        self._validate_limits(min_tokens, max_tokens, overlap_tokens)
        units = self._build_units(pages)
        if not units:
            return []

        ranges = self._build_ranges(units, min_tokens, max_tokens, overlap_tokens)
        chunks: list[ChunkedText] = []

        for index, (start, end) in enumerate(ranges, start=1):
            selected = units[start:end]
            text = self._render(selected, include_page_markers)
            section_title = next(
                (unit.section_title for unit in selected if unit.section_title), None
            )
            token_count = self.count_tokens(text)
            digest = hashlib.sha256(
                f"{document_id}:{index}:{text}".encode("utf-8")
            ).hexdigest()[:24]

            chunks.append(
                {
                    "chunk_id": digest,
                    "document_id": document_id,
                    "text": text,
                    "page_start": selected[0].page_number,
                    "page_end": selected[-1].page_number,
                    "chunk_index": index,
                    "token_count": token_count,
                    "section_title": section_title,
                }
            )

        return chunks

    @classmethod
    def count_tokens(cls, text: str) -> int:
        """Harici modele bağlı olmayan, deterministik yaklaşık token sayımı."""
        return len(cls._TOKEN_PATTERN.findall(text))

    @staticmethod
    def _validate_limits(min_tokens: int, max_tokens: int, overlap_tokens: int) -> None:
        if min_tokens < 1 or max_tokens < min_tokens:
            raise ValueError("Token sınırları geçersiz.")
        if not 80 <= overlap_tokens <= 150:
            raise ValueError("Overlap 80 ile 150 token arasında olmalıdır.")
        if overlap_tokens >= min_tokens:
            raise ValueError("Overlap minimum chunk boyutundan küçük olmalıdır.")

    def _build_units(self, pages: Sequence[ExtractedPage]) -> list[_TextUnit]:
        units: list[_TextUnit] = []
        current_section: str | None = None

        for page in sorted(pages, key=lambda item: item["page_number"]):
            for line in (line.strip() for line in page["text"].splitlines()):
                if not line:
                    continue
                if self._is_heading(line):
                    current_section = line
                    units.append(
                        _TextUnit(line, page["page_number"], current_section, self.count_tokens(line))
                    )
                    continue

                for sentence in self._SENTENCE_BOUNDARY.split(line):
                    sentence = sentence.strip()
                    if sentence:
                        units.append(
                            _TextUnit(
                                sentence,
                                page["page_number"],
                                current_section,
                                self.count_tokens(sentence),
                            )
                        )

        return units

    def _build_ranges(
        self,
        units: Sequence[_TextUnit],
        min_tokens: int,
        max_tokens: int,
        overlap_tokens: int,
    ) -> list[tuple[int, int]]:
        ranges: list[tuple[int, int]] = []
        start = 0

        while start < len(units):
            end = start
            token_total = 0
            current_page: int | None = None
            while end < len(units):
                next_count = units[end].token_count
                if units[end].page_number != current_page:
                    next_count += self.count_tokens(
                        f"[Sayfa {units[end].page_number}]"
                    )
                if end > start and token_total + next_count > max_tokens:
                    break
                token_total += next_count
                current_page = units[end].page_number
                end += 1

            if end == len(units):
                ranges.append((start, end))
                break

            ranges.append((start, end))
            next_start = end
            overlap_total = 0
            while next_start > start and overlap_total < overlap_tokens:
                next_start -= 1
                overlap_total += units[next_start].token_count

            # Çok uzun tek cümlede ilerlemenin durmasını engeller.
            start = next_start if next_start > start else end

        return self._rebalance_short_final_chunk(
            units, ranges, min_tokens, max_tokens, overlap_tokens
        )

    def _rebalance_short_final_chunk(
        self,
        units: Sequence[_TextUnit],
        ranges: list[tuple[int, int]],
        min_tokens: int,
        max_tokens: int,
        overlap_tokens: int,
    ) -> list[tuple[int, int]]:
        if len(ranges) < 2:
            return ranges

        last_start, last_end = ranges[-1]
        if self._rendered_token_count(units, last_start, last_end) >= min_tokens:
            return ranges

        previous_start, previous_end = ranges[-2]
        boundary = previous_end

        while boundary > previous_start + 1:
            boundary -= 1
            new_last_start = boundary
            overlap_total = 0
            while new_last_start > previous_start and overlap_total < overlap_tokens:
                new_last_start -= 1
                overlap_total += units[new_last_start].token_count

            previous_tokens = self._rendered_token_count(units, previous_start, boundary)
            last_tokens = self._rendered_token_count(units, new_last_start, last_end)
            if (
                min_tokens <= previous_tokens <= max_tokens
                and min_tokens <= last_tokens <= max_tokens
            ):
                ranges[-2] = (previous_start, boundary)
                ranges[-1] = (new_last_start, last_end)
                return ranges

        # İki geçerli chunk oluşturulamıyorsa kısa parça üretmek yerine birleştir.
        ranges[-2:] = [(previous_start, last_end)]
        return ranges

    @staticmethod
    def _unit_token_count(
        units: Sequence[_TextUnit], start: int, end: int
    ) -> int:
        return sum(unit.token_count for unit in units[start:end])

    def _rendered_token_count(
        self, units: Sequence[_TextUnit], start: int, end: int
    ) -> int:
        return self.count_tokens(self._render(units[start:end], True))

    @staticmethod
    def _render(units: Sequence[_TextUnit], include_page_markers: bool) -> str:
        parts: list[str] = []
        current_page: int | None = None

        for unit in units:
            if include_page_markers and unit.page_number != current_page:
                parts.append(f"[Sayfa {unit.page_number}]")
                current_page = unit.page_number
            parts.append(unit.text)

        return "\n".join(parts).strip()

    @staticmethod
    def _is_heading(line: str) -> bool:
        if len(line) > 120 or len(line.split()) > 14:
            return False
        if re.match(r"^(?:#{1,6}\s+|\d+(?:\.\d+)*[.)]?\s+)", line):
            return True
        letters = [character for character in line if character.isalpha()]
        if letters and len(letters) >= 3 and all(character.isupper() for character in letters):
            return True
        return line.endswith(":")
