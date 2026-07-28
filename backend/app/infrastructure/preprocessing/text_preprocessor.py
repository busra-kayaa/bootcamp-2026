import re
import unicodedata


class TextPreprocessor:
    """Belgeden çıkarılan metni, anlamını koruyarak temizler."""

    def clean(self, text: str) -> str:
        if not text:
            return ""

        # Unicode karakterlerini standartlaştırır.
        text = unicodedata.normalize("NFKC", text)

        # Görünmeyen ve sorunlu boşluk karakterlerini temizler.
        text = text.replace("\u00a0", " ")

        # Satır sonlarını standartlaştırır.
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Biçimlendirme işaretleri ve kontrol karakterlerini kaldırır;
        # paragraf yapısı için gerekli satır sonu ve sekme korunur.
        text = "".join(
            character
            for character in text
            if unicodedata.category(character) not in {"Cf", "Cc"}
            or character in {"\n", "\t"}
        )

        # Yalnızca açık satır-sonu bölünmelerini birleştirir:
        # "dokü-\nman" -> "doküman". Normal "e-posta" gibi kelimeler korunur.
        text = re.sub(
            r"(?<=[^\W\d_])[-‐‑][ \t]*\n[ \t]*(?=[a-zçğıiöşü])",
            "",
            text,
            flags=re.UNICODE,
        )

        # Satır içindeki fazla boşlukları tek boşluğa indirir.
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)

        # Paragraf ayrımını korur, yalnızca aşırı boş satırları azaltır.
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
