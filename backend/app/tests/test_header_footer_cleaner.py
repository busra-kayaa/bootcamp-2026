from app.infrastructure.preprocessing.header_footer_cleaner import HeaderFooterCleaner


def test_removes_repeated_headers_footers_and_page_numbers() -> None:
    pages = [
        {
            "page_number": number,
            "text": f"ACME Gizli Belge\nBölüm {number}\nSayfa metni {number}\nSayfa {number} / 3",
            "extraction_method": "pdfplumber",
        }
        for number in range(1, 4)
    ]

    cleaned = HeaderFooterCleaner(boundary_lines=2).clean(pages)

    assert sum(page["text"].count("ACME Gizli Belge") for page in cleaned) == 1
    assert all("Sayfa " not in page["text"] for page in cleaned)
    assert "Sayfa metni 1" in cleaned[0]["text"]


def test_keeps_single_page_unchanged() -> None:
    pages = [
        {
            "page_number": 1,
            "text": "Başlık\nGövde\nSayfa 1",
            "extraction_method": "pdfplumber",
        }
    ]

    assert HeaderFooterCleaner().clean(pages) == pages


def test_does_not_remove_repeated_body_line() -> None:
    pages = [
        {
            "page_number": number,
            "text": f"Farklı başlık {number}\nOrtak gövde cümlesi\nFarklı son {number}",
            "extraction_method": "pdfplumber",
        }
        for number in range(1, 4)
    ]

    cleaned = HeaderFooterCleaner(boundary_lines=1).clean(pages)

    assert all("Ortak gövde cümlesi" in page["text"] for page in cleaned)
