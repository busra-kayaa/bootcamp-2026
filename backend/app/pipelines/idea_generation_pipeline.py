import json
from typing import List
from pydantic import BaseModel, Field

# Altyapı sağlayıcıları
from app.infrastructure.vector_store.pgvector_store import PGVectorStore
from app.infrastructure.llm.llm_provider import GroqLLMProvider
from app.infrastructure.embeddings.sentence_transformer_provider import SentenceTransformerProvider
from app.infrastructure.llm.structured_output_parser import StructuredOutputParser

# Frontend ile %100 uyumlu şemamızı içe aktarıyoruz (IDEA_AGENT_PROMPT importunu sildik)
from app.pipelines.requirement_analysis_pipeline import IdeaSchema 

class IdeaGenerationResponse(BaseModel):
    ideas: List[IdeaSchema] = Field(..., description="Şartnameye uygun KESİNLİKLE VE TAM OLARAK 3 FARKLI proje fikri.")

class IdeaGenerationPipeline:
    def __init__(
        self,
        vector_store: PGVectorStore,
        llm_provider: GroqLLMProvider,
        embedding_provider: SentenceTransformerProvider
    ):
        self.vector_store = vector_store
        self.llm_provider = llm_provider
        self.embedding_provider = embedding_provider

    async def execute(self, document_id: int) -> list:
        """
        Şartnamenin tamamını değil, yalnızca proje fikirleri üretmek için 
        hedef odaklı RAG araması yapar ve 3 yeni fikir döndürür.
        """
        
        query = "Yarışmanın temel amacı, beklenen proje çıktıları, yenilikçi sistemler ve değerlendirme kriterleri nelerdir?"
        query_embedding = await self.embedding_provider.embed_text(query)

        relevant_chunks = await self.vector_store.similarity_search(
            document_id=document_id,
            query_embedding=query_embedding,
            top_k=7
        )

        context_text = "\n\n".join(
            [f"[Kaynak ID: {c['chunk_id']}] Sayfa {c['page_start']}: {c['text']}" for c in relevant_chunks]
        )

        user_prompt = f"""
        Şartnameden Çekilen İlgili Orijinal Bölümler (RAG Bağlamı):
        {context_text}

        Lütfen yukarıdaki bağlama tamamen uygun, inovatif ve daha önce üretilmemiş KESİNLİKLE TAM OLARAK 3 ADET proje fikri üret. 
        Fikirlerin açıklamasına (description) kaynak ID veya sayfa numarası ekleme.
        """

        # YENİ EKLENEN ÇOK SIKI SYSTEM PROMPT
        # JSON anahtarlarının Türkçeye çevrilmesini kesin ve net bir dille yasaklıyoruz.
        strict_system_prompt = """
        Sen, savunma sanayii ve ileri teknoloji projelerinde uzman kıdemli bir Sistem ve Proje Mühendisliği uzmanısın.
        SADECE aşağıdaki JSON formatında ve İNGİLİZCE anahtarlar (keys) kullanarak yanıt ver. 
        Anahtarları (keys) KESİNLİKLE Türkçeye çevirme. Örneğin 'proje_adi' YAZMA, 'title' YAZ.

        {
          "ideas": [
            {
              "title": "Projenin Adı",
              "description": "Projenin detayı",
              "score": 90,
              "aiContribution": "Yapay zeka katkısı"
            }
          ]
        }
        """

        raw_llm_output = await self.llm_provider.generate_structured(
            system_prompt=strict_system_prompt,
            user_prompt=user_prompt,
            response_schema=IdeaGenerationResponse
        )

        validated_data = StructuredOutputParser.parse(
            llm_output=raw_llm_output,
            schema=IdeaGenerationResponse
        )

        return validated_data.model_dump().get("ideas", [])