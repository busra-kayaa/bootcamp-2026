import asyncio
import sys
from pathlib import Path

from app.pipelines.document_ingestion_pipeline import DocumentIngestionPipeline


async def main() -> None:
    sample_name = sys.argv[1] if len(sys.argv) > 1 else "samples/ornek.pdf"
    document_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    file_path = (Path(__file__).resolve().parent / sample_name).resolve()

    print(f"Açılan dosya: {file_path}")
    print(f"Dosya var mı: {file_path.exists()}")

    pipeline = DocumentIngestionPipeline()
    result = await pipeline.process(document_id=document_id, file_path=str(file_path))
    chunks = result["chunks"]

    print("=" * 70)
    print("INGESTION PIPELINE SONUCU")
    print(f"Document ID: {result['document_id']}")
    print(f"Sayfa sayısı: {result['page_count']}")
    print(f"Temiz metin karakter sayısı: {result['character_count']}")
    print(f"Çıkarma yöntemi: {result['extraction_method']}")
    print(f"Chunk sayısı: {len(chunks)}")

    for chunk in chunks:
        preview = chunk["text"].replace("\n", " ")[:180]
        print("-" * 70)
        print(f"Chunk index: {chunk['chunk_index']}")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Token: {chunk['token_count']}")
        print(f"Sayfa: {chunk['page_start']} - {chunk['page_end']}")
        print(f"Bölüm: {chunk['section_title'] or '-'}")
        print(f"Önizleme: {preview}")

    invalid_chunks = [
        chunk
        for chunk in chunks
        if not chunk["text"].strip()
        or (len(chunks) > 1 and not 500 <= chunk["token_count"] <= 900)
    ]
    print("=" * 70)
    print(
        "KALİTE KONTROLÜ: BAŞARILI"
        if chunks and not invalid_chunks
        else "KALİTE KONTROLÜ: BAŞARISIZ"
    )


if __name__ == "__main__":
    asyncio.run(main())
