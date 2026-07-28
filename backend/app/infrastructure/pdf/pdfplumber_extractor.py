from pathlib import Path

import pdfplumber

from .base import ExtractedPage
from .ocr_extractor import OCRExtractor


class PdfPlumberExtractor:
    """
    Metin tabanlı PDF dosyalarından sayfa sayfa metin çıkarır.

    Bu sınıf taranmış, görsel tabanlı PDF'lerde başarılı olmayabilir.
    Görsel tabanlı sayfalar daha sonra OCR modülüne yönlendirilecektir.
    """

    def __init__(self, ocr_extractor: OCRExtractor | None = None) -> None:
        self._ocr_extractor = ocr_extractor or OCRExtractor()

    def extract(self, file_path: str | Path) -> list[ExtractedPage]:
        """
        Verilen PDF dosyasını açar ve her sayfanın metnini ayrı olarak döndürür.

        Args:
            file_path: Okunacak PDF dosyasının yolu.

        Returns:
            Sayfa numarası, metin ve çıkarma yöntemini içeren liste.

        Raises:
            FileNotFoundError: Dosya bulunamazsa.
            ValueError: Dosya PDF değilse, boşsa veya sayfa içermiyorsa.
            RuntimeError: PDF okunurken beklenmeyen bir hata oluşursa.
        """

        path = Path(file_path)

        self._validate_file(path)

        extracted_pages: list[ExtractedPage] = []
        ocr_pages_by_number: dict[int, ExtractedPage] | None = None

        try:
            with pdfplumber.open(path) as pdf:
                if len(pdf.pages) == 0:
                    raise ValueError("PDF içerisinde herhangi bir sayfa bulunamadı.")

                for page_number, page in enumerate(pdf.pages, start=1):
                    extracted_text = page.extract_text() or ""

                    if extracted_text.strip():
                        extracted_pages.append(
                            {
                                "page_number": page_number,
                                "text": extracted_text.strip(),
                                "extraction_method": "pdfplumber",
                            }
                        )
                        continue

                    if ocr_pages_by_number is None:
                        ocr_pages_by_number = {
                            ocr_page["page_number"]: ocr_page
                            for ocr_page in self._ocr_extractor.extract(path)
                        }

                    ocr_page = ocr_pages_by_number.get(page_number)

                    if ocr_page is not None:
                        extracted_pages.append(ocr_page)
                        continue

                    extracted_pages.append(
                        {
                            "page_number": page_number,
                            "text": "",
                            "extraction_method": "ocr",
                        }
                    )

        except ValueError:
            raise

        except RuntimeError:
            raise

        except Exception as exc:
            raise RuntimeError(
                f"PDF dosyası okunurken hata oluştu: {path.name}"
            ) from exc

        if not any(page["text"].strip() for page in extracted_pages):
            raise ValueError("PDF içerisinde okunabilir metin bulunamadı.")

        return extracted_pages

    @staticmethod
    def _validate_file(path: Path) -> None:
        """
        PDF dosyasını açmadan önce temel kontrolleri gerçekleştirir.
        """

        if not path.exists():
            raise FileNotFoundError(f"PDF dosyası bulunamadı: {path}")

        if not path.is_file():
            raise ValueError(f"Verilen yol bir dosyaya ait değil: {path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                "Desteklenmeyen dosya türü. Yalnızca PDF dosyaları kabul edilir."
            )

        if path.stat().st_size == 0:
            raise ValueError("PDF dosyası boş.")

        # Yalnızca uzantıyı değil, dosyanın gerçekten PDF olup olmadığını da kontrol et.
        with path.open("rb") as file:
            if b"%PDF-" not in file.read(1024):
                raise ValueError("Dosya geçerli bir PDF formatında değil.")
