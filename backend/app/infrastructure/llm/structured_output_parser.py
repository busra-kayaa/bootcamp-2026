import json
import re
from pydantic import ValidationError

class StructuredOutputParser:
    @staticmethod
    def parse(llm_output: str, schema: type):
        """
        LLM'den gelen metni temizler, JSON'a çevirir ve Pydantic şemasıyla doğrular.
        """
        # 1. Markdown kod bloklarını temizleme (```json ... ```)
        cleaned_text = re.sub(r"```json\s*", "", llm_output, flags=re.IGNORECASE)
        cleaned_text = re.sub(r"```\s*", "", cleaned_text)
        cleaned_text = cleaned_text.strip()
        
        # 2. String ifadeyi JSON (dictionary) formatına dönüştürme
        try:
            parsed_json = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM çıktısı ayıklanamadı, geçerli bir JSON değil: {e}\nÇıktı: {llm_output}")
            
        # 3. Pydantic modeli ile doğrulatma (Eksik alan veya yanlış tip tespiti)
        try:
            validated_data = schema(**parsed_json)
            return validated_data
        except ValidationError as e:
            raise ValueError(f"LLM çıktısı beklenen Pydantic şemasına uymuyor: {e}")