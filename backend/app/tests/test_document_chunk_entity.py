from dataclasses import asdict, is_dataclass

from app.domain.entities.document_chunk import DocumentChunk


def test_document_chunk_is_an_orm_independent_dataclass() -> None:
    chunk = DocumentChunk(
        chunk_id="doc-7-chunk-1",
        document_id=7,
        text="Birinci chunk metni.",
        chunk_index=1,
        page_start=2,
        page_end=3,
        token_count=520,
        section_title="Proje Kapsamı",
    )

    assert is_dataclass(chunk)
    assert asdict(chunk) == {
        "chunk_id": "doc-7-chunk-1",
        "document_id": 7,
        "text": "Birinci chunk metni.",
        "chunk_index": 1,
        "page_start": 2,
        "page_end": 3,
        "token_count": 520,
        "section_title": "Proje Kapsamı",
    }


def test_section_title_is_optional() -> None:
    chunk = DocumentChunk(
        chunk_id="chunk-1",
        document_id=1,
        text="Başlıksız metin.",
        chunk_index=1,
        page_start=1,
        page_end=1,
        token_count=3,
    )

    assert chunk.section_title is None
