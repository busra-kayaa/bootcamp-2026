import re
import unicodedata


class TextPreprocessor:
    """PDF'den çıkarılan ham metni analiz öncesinde temizler."""

    def clean(self, text: str) -> str:
        if not text:
            return ""

        # Unicode karakterlerini standartlaştırır.
        text = unicodedata.normalize("NFKC", text)

        # Görünmeyen ve sorunlu boşluk karakterlerini temizler.
        text = text.replace("\u00a0", " ")
        text = text.replace("\u200b", "")
        text = text.replace("\ufeff", "")

        # Satır sonlarını standartlaştırır.
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Satır içindeki fazla boşlukları tek boşluğa indirir.
        text = re.sub(r"[ \t]+", " ", text)

        # Üç veya daha fazla satır boşluğunu iki satıra indirir.
        text = re.sub(r"\n{3,}", "\n\n", text)

        cleaned_lines: list[str] = []

        for line in text.splitlines():
            cleaned_line = line.strip()

            if cleaned_line:
                cleaned_lines.append(cleaned_line)

        return "\n".join(cleaned_lines).strip()
