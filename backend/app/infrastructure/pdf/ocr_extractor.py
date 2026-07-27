from pathlib import Path

import easyocr
import pypdfium2
import numpy as np
import torch

from .base import ExtractedPage


class OCRExtractor:
    """
    PDF sayfalarını görüntüye çevirip OCR ile metin çıkarır.
    """

    def __init__(
        self,
        languages: list[str] | None = None,
        use_gpu: bool | None = None,
    ) -> None:
        self._languages = languages or ["tr", "en"]
        self._use_gpu = torch.cuda.is_available() if use_gpu is None else use_gpu
        self._reader: easyocr.Reader | None = None

    def _get_reader(self) -> easyocr.Reader:
        if self._reader is None:
            try:
                self._reader = easyocr.Reader(
                    self._languages,
                    gpu=self._use_gpu,
                    verbose=False,
                )
            except Exception as exc:
                raise RuntimeError(
                    "OCR motoru başlatılamadı. easyocr ve bağımlılıkları kurulu olmalı."
                ) from exc

        return self._reader

    def extract(self, file_path: str | Path) -> list[ExtractedPage]:
        path = Path(file_path)

        self._validate_file(path)

        extracted_pages: list[ExtractedPage] = []

        try:
            pdf = pypdfium2.PdfDocument(str(path))
        except Exception as exc:
            raise RuntimeError(f"PDF OCR için açılamadı: {path.name}") from exc

        try:
            page_count = len(pdf)

            if page_count == 0:
                raise ValueError("PDF içerisinde herhangi bir sayfa bulunamadı.")

            reader = self._get_reader()

            for page_number in range(1, page_count + 1):
                page = pdf.get_page(page_number - 1)

                try:
                    bitmap = page.render(scale=2.0)
                    image = bitmap.to_pil()
                    image_array = np.array(image)
                    extracted_lines = reader.readtext(
                        image_array,
                        detail=0,
                        paragraph=True,
                    )
                    extracted_text = " ".join(extracted_lines).strip()
                finally:
                    page.close()

                extracted_pages.append(
                    {
                        "page_number": page_number,
                        "text": extracted_text,
                        "extraction_method": "ocr",
                    }
                )

        except ValueError:
            raise

        except Exception as exc:
            raise RuntimeError(
                f"PDF OCR ile okunurken hata oluştu: {path.name}"
            ) from exc

        finally:
            pdf.close()

        return extracted_pages

    @staticmethod
    def _validate_file(path: Path) -> None:
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
