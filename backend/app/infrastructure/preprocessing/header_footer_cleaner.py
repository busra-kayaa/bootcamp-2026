from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.infrastructure.pdf.base import ExtractedPage


class HeaderFooterCleaner:
    """Sayfalarda tekrarlanan üstbilgi ve altbilgi satırlarını temizler."""

    def __init__(self, boundary_lines: int = 3, repeat_ratio: float = 0.6) -> None:
        if boundary_lines < 1:
            raise ValueError("boundary_lines en az 1 olmalıdır.")
        if not 0 < repeat_ratio <= 1:
            raise ValueError("repeat_ratio 0 ile 1 arasında olmalıdır.")

        self._boundary_lines = boundary_lines
        self._repeat_ratio = repeat_ratio

    def clean(self, pages: Sequence[ExtractedPage]) -> list[ExtractedPage]:
        copied_pages = [dict(page) for page in pages]
        content_pages = [page for page in copied_pages if page["text"].strip()]

        # Tek sayfada tekrar bilgisi olmadığı için güvenli bir temizlik yapılamaz.
        if len(content_pages) < 2:
            return copied_pages

        minimum_repeats = max(2, math.ceil(len(content_pages) * self._repeat_ratio))
        header_counts: Counter[str] = Counter()
        footer_counts: Counter[str] = Counter()

        for page in content_pages:
            lines = self._non_empty_lines(page["text"])
            header_counts.update(set(map(self._normalize, lines[: self._boundary_lines])))
            footer_counts.update(set(map(self._normalize, lines[-self._boundary_lines :])))

        repeated_headers = {
            line for line, count in header_counts.items() if line and count >= minimum_repeats
        }
        repeated_footers = {
            line for line, count in footer_counts.items() if line and count >= minimum_repeats
        }
        preserved_repeated_lines: set[str] = set()

        for page in copied_pages:
            lines = self._non_empty_lines(page["text"])
            last_boundary_start = max(0, len(lines) - self._boundary_lines)
            kept_lines = []

            for index, line in enumerate(lines):
                normalized = self._normalize(line)
                is_header = index < self._boundary_lines and normalized in repeated_headers
                is_footer = index >= last_boundary_start and normalized in repeated_footers

                if not is_header and not is_footer:
                    kept_lines.append(line)
                    continue

                # Şirket adı, belge başlığı veya gizlilik ibaresi gibi anlamlı
                # sabit metinleri kaybetme; ilk geçişi koruyup yalnızca tekrarları sil.
                # Saf sayfa numaralarının ise bilgi değeri olmadığından tamamını kaldır.
                if (
                    not self._is_page_number(line)
                    and normalized not in preserved_repeated_lines
                ):
                    kept_lines.append(line)
                    preserved_repeated_lines.add(normalized)

            page["text"] = "\n".join(kept_lines).strip()

        return copied_pages

    @staticmethod
    def _non_empty_lines(text: str) -> list[str]:
        return [line.strip() for line in text.splitlines() if line.strip()]

    @staticmethod
    def _normalize(line: str) -> str:
        normalized = unicodedata.normalize("NFKC", line).casefold()
        normalized = re.sub(r"\s+", " ", normalized).strip()

        # Değişen rakamları sadece sayfa numarası biçimlerinde şablonlaştır.
        # Bölüm 1 / Bölüm 2 gibi gerçek başlıklar bu sayede korunur.
        return (
            re.sub(r"\d+", "#", normalized)
            if HeaderFooterCleaner._is_page_number(normalized)
            else normalized
        )

    @staticmethod
    def _is_page_number(line: str) -> bool:
        normalized = unicodedata.normalize("NFKC", line).casefold().strip()
        return bool(
            re.search(r"\b(?:sayfa|page|say)\b", normalized)
            or re.fullmatch(r"[\d\s/|._-]+", normalized)
        )
