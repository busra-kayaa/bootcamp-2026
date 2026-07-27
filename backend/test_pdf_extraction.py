from pathlib import Path
import sys

from app.infrastructure.chunking.token_chunker import TokenChunker
from app.infrastructure.pdf.pdfplumber_extractor import PdfPlumberExtractor
from app.infrastructure.pdf.text_combiner import TextCombiner


def main() -> None:
    sample_name = sys.argv[1] if len(sys.argv) > 1 else "samples/ornek.pdf"
    file_path = (Path(__file__).resolve().parent / sample_name).resolve()

    print(f"Açılan dosya: {file_path}")
    print(f"Dosya var mı: {file_path.exists()}")

    if not file_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")

    print(f"Dosya boyutu: {file_path.stat().st_size} bayt")

    extractor = PdfPlumberExtractor()
    pages = extractor.extract(file_path)
    combiner = TextCombiner()
    combined_text = combiner.combine(pages)
    chunker = TokenChunker()
    chunks = chunker.chunk(pages, max_chars=1200)

    print(f"Toplam sayfa sayısı: {len(pages)}")

    print("=" * 60)
    print("BİRLEŞİK METİN")
    print(f"Toplam karakter sayısı: {len(combined_text)}")
    print(combined_text or "METİN BULUNAMADI")

    print("=" * 60)
    print("CHUNK'LAR")
    print(f"Chunk sayısı: {len(chunks)}")

    for chunk in chunks:
        print("-" * 60)
        print(f"Chunk no: {chunk['chunk_index']}")
        print(f"Sayfa aralığı: {chunk['page_start']} - {chunk['page_end']}")
        print(f"Sayfalar: {chunk['page_numbers']}")
        print(f"Kaynaklar: {chunk['extraction_methods']}")
        print(f"Karakter sayısı: {chunk['character_count']}")
        print(chunk['text'])


if __name__ == "__main__":
    main()
