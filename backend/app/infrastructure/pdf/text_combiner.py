from collections.abc import Sequence

from .base import ExtractedPage


class TextCombiner:
    """
    Sayfa bazlı çıkarılmış metinleri tek bir düzenli metin halinde birleştirir.
    """

    def combine(
        self,
        pages: Sequence[ExtractedPage],
        *,
        include_page_markers: bool = True,
    ) -> str:
        ordered_pages = sorted(pages, key=lambda page: page["page_number"])
        combined_parts: list[str] = []

        for page in ordered_pages:
            page_text = page["text"].strip()

            if not page_text:
                continue

            if include_page_markers:
                combined_parts.append(
                    f"[Sayfa {page['page_number']} | {page['extraction_method']}]\n{page_text}"
                )
            else:
                combined_parts.append(page_text)

        return "\n\n".join(combined_parts)
