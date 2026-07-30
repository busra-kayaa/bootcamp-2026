import os
import json
from dotenv import load_dotenv
from groq import AsyncGroq
from app.domain.interfaces.llm_provider_interface import LLMProviderInterface

# Ortam değişkenlerini garantili okumak için ekledik
load_dotenv()

class GroqLLMProvider(LLMProviderInterface):
    def __init__(self):
        # 1. .env dosyasında oluşturduğumuz GROQ_API_KEY'i çekecek şekilde düzelttik
        api_key = os.getenv("GROQ_API_KEY")
        
        # 2. .env'deki gpt-4o modeli Groq'da çalışmayacağı için 
        # Groq'un çok hızlı ve güçlü modelini doğrudan buraya sabitliyoruz
        self.model = "llama-3.3-70b-versatile"
        
        self.client = AsyncGroq(api_key=api_key)

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        response = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=self.model,
            temperature=temperature
        )
        return response.choices[0].message.content

    async def generate_structured(self, system_prompt: str, user_prompt: str, response_schema: type):
        # 1. Pydantic şemasından beklenen JSON formatını otomatik olarak çekiyoruz
        schema_format = json.dumps(response_schema.model_json_schema(), ensure_ascii=False)
        
        # 2. JSON modunu ve beklenen kesin yapıyı güvenceye almak için prompt'a çok katı bir ekleme yapıyoruz
        json_system_prompt = system_prompt + f"\n\nLütfen cevabını SADECE aşağıdaki JSON şemasına (schema) birebir uyarak ver. JSON dışında hiçbir metin veya açıklama ekleme:\n{schema_format}"
        
        response = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": json_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=self.model,
            temperature=0.1, # Yapılandırılmış çıktılar için düşük temperature şarttır
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return content