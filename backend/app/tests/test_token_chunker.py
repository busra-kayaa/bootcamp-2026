from app.infrastructure.chunking.token_chunker import TokenChunker


def _long_pages(sentence_count: int = 240) -> list[dict]:
    sentences = [
        f"Bu {index} numaralı gereksinim cümlesidir ve anlamlı biçimde tamamlanır."
        for index in range(sentence_count)
    ]
    midpoint = len(sentences) // 2
    return [
        {
            "page_number": 1,
            "text": "1. PROJE KAPSAMI\n" + " ".join(sentences[:midpoint]),
            "extraction_method": "pdfplumber",
        },
        {
            "page_number": 2,
            "text": " ".join(sentences[midpoint:]),
            "extraction_method": "pdfplumber",
        },
    ]


def test_chunks_have_required_fields_and_valid_sizes() -> None:
    chunks = TokenChunker().chunk(_long_pages(), document_id=42)

    assert len(chunks) > 1
    assert all(
        {
            "chunk_id",
            "document_id",
            "text",
            "page_start",
            "page_end",
            "chunk_index",
            "token_count",
            "section_title",
        }
        == set(chunk)
        for chunk in chunks
    )
    assert all(chunk["document_id"] == 42 for chunk in chunks)
    assert all(chunk["text"].strip() for chunk in chunks)
    assert all(chunk["token_count"] >= 500 for chunk in chunks)
    assert all(chunk["token_count"] <= 900 for chunk in chunks)
    assert [chunk["chunk_index"] for chunk in chunks] == list(
        range(1, len(chunks) + 1)
    )


def test_preserves_sentence_page_and_section_information() -> None:
    chunks = TokenChunker().chunk(_long_pages(), document_id=7)

    assert chunks[0]["section_title"] == "1. PROJE KAPSAMI"
    assert all("[Sayfa " in chunk["text"] for chunk in chunks)
    assert all(chunk["text"].rstrip().endswith(".") for chunk in chunks)
    assert chunks[0]["page_start"] == 1
    assert chunks[-1]["page_end"] == 2


def test_short_document_is_kept_as_one_non_empty_chunk() -> None:
    pages = [
        {
            "page_number": 1,
            "text": "Kısa fakat anlamlı bir belge.",
            "extraction_method": "python-docx",
        }
    ]

    chunks = TokenChunker().chunk(pages, document_id=3)

    assert len(chunks) == 1
    assert chunks[0]["text"]
