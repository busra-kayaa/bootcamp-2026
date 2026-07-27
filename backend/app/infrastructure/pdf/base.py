from typing import TypedDict


class ExtractedPage(TypedDict):
    """
    PDF'den çıkarılan tek bir sayfanın veri yapısı.
    """

    page_number: int
    text: str
    extraction_method: str
