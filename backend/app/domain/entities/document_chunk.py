from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """Veritabanı ve ORM katmanından bağımsız doküman parçası."""

    chunk_id: str
    document_id: int
    text: str
    chunk_index: int
    page_start: int
    page_end: int
    token_count: int
    section_title: str | None = None
