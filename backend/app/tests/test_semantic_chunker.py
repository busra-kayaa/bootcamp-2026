from app.infrastructure.chunking.semantic_chunker import SemanticChunker


def test_recognizes_heading_hierarchy_and_keeps_related_list_items() -> None:
    text = """1. PROJE KAPSAMI

Bu bölümde uygulanacak kurallar şunlardır:

a) Birinci madde kendi açıklamasıyla birliktedir.

b) İkinci madde birinci maddeyle aynı anlam grubundadır.

1.1 Teknik Gereksinimler

Sistem güvenli ve izlenebilir olmalıdır."""
    pages = [
        {"page_number": 1, "text": text, "extraction_method": "pdfplumber"}
    ]

    chunker = SemanticChunker()
    units = chunker._build_units(pages)

    related = next(unit for unit in units if "Birinci madde" in unit.text)
    assert "kurallar şunlardır:" in related.text
    assert "İkinci madde" in related.text
    assert units[-1].section_title == (
        "1. PROJE KAPSAMI > 1.1 Teknik Gereksinimler"
    )


def test_recognizes_article_heading() -> None:
    pages = [
        {
            "page_number": 1,
            "text": "MADDE 3 - Başvuru Koşulları\nBaşvuru zamanında yapılmalıdır.",
            "extraction_method": "pdfplumber",
        }
    ]

    units = SemanticChunker()._build_units(pages)

    assert units[-1].section_title == "MADDE 3 - Başvuru Koşulları"


def test_does_not_treat_date_line_as_numbered_heading() -> None:
    chunker = SemanticChunker()

    assert chunker._heading_level("5 Temmuz 2026 20 Temmuz 2026 20.00") is None
    assert chunker._heading_level("1. Proje Kapsamı") == 1
    assert chunker._heading_level("1.2 Teknik Gereksinimler") == 2


def test_large_section_is_split_without_cutting_sentences() -> None:
    sentences = [
        f"Gereksinim {index} eksiksiz bir cümle olarak sona erer."
        for index in range(220)
    ]
    pages = [
        {
            "page_number": 1,
            "text": "2. UYGULAMA\n\n" + " ".join(sentences),
            "extraction_method": "pdfplumber",
        }
    ]

    chunks = SemanticChunker().chunk(pages, document_id=10)

    assert len(chunks) > 1
    assert all(500 <= chunk["token_count"] <= 900 for chunk in chunks)
    assert all(chunk["text"].endswith(".") for chunk in chunks)
    assert all(chunk["section_title"] == "2. UYGULAMA" for chunk in chunks)
