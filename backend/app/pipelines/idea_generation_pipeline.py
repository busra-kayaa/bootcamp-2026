import json
from typing import List
from pydantic import BaseModel

# Altyapı sağlayıcıları
from app.infrastructure.vector_store.pgvector_store import PGVectorStore
from app.infrastructure.llm.llm_provider import GroqLLMProvider
from app.infrastructure.embeddings.sentence_transformer_provider import SentenceTransformerProvider
from app.infrastructure.llm.structured_output_parser import StructuredOutputParser

# Takım arkadaşın Petek'in hazırladığı prompt (İçe aktarma yolu projenize göre değişebilir)
from app.prompts.idea_prompts import IDEA_AGENT_PROMPT

# ---------------------------------------------------------
# Çıktı Formatını Zorlamak İçin Pydantic Şemaları[cite: 3]
# ---------------------------------------------------------
class ProjectIdeaSchema(BaseModel):
    name: str
    description: str
    suitability_reason: str
    ai_contribution_score: int
    feasibility_score: int
    overall_score: int
    advantages: List[str]
    disadvantages: List[str]
    source_chunk_ids: List[str]

class IdeaGenerationResponse(BaseModel):
    ideas: List[ProjectIdeaSchema]


# ---------------------------------------------------------
# Ana Pipeline Sınıfı
# ---------------------------------------------------------
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

    async def execute(self, document_id: int, rules_and_summary: str) -> dict:
        """
        Şartname kurallarını ve özetini alarak 3 adet proje fikri üretir[cite: 3].
        """
        
        # 1. RAG için arama sorgusunu vektöre çevir
        # Şartnamedeki "amaç, beklenti ve hedefler" kısmını bulmak için hedefli bir sorgu atıyoruz
        query = "Yarışmanın temel amacı, beklenen proje çıktıları, yenilikçi sistemler ve değerlendirme kriterleri nelerdir?"
        query_embedding = await self.embedding_provider.embed_text(query)

        # 2. Veritabanından (PGVector) en alakalı parçaları (chunk) getir[cite: 3]
        relevant_chunks = await self.vector_store.similarity_search(
            document_id=document_id,
            query_embedding=query_embedding,
            top_k=7
        )

        # 3. LLM için bağlamı (context) kaynak ID'leriyle birlikte hazırla
        context_text = "\n\n".join(
            [f"[Kaynak ID: {c['chunk_id']}] Sayfa {c['page_start']}: {c['text']}" for c in relevant_chunks]
        )

        # 4. LLM'e gidecek kullanıcı mesajını oluştur
        user_prompt = f"""
        Şartnameden Çıkarılan Temel Kurallar ve Özet:
        {rules_and_summary}

        Şartnameden Çekilen İlgili Orijinal Bölümler (RAG Bağlamı):
        {context_text}

        Lütfen yukarıdaki kurallara ve bağlama tamamen uygun 3 adet proje fikri üret. 
        Her fikrin şartnameyle ilişkisini 'source_chunk_ids' alanında belirt[cite: 3].
        """

        # 5. Groq LLM'i JSON formatında cevap üretmeye zorlayarak çağır[cite: 3]
        raw_llm_output = await self.llm_provider.generate_structured(
            system_prompt=IDEA_AGENT_PROMPT,
            user_prompt=user_prompt,
            response_schema=IdeaGenerationResponse
        )

        # 6. Çıktıyı Markdown'dan temizle, JSON yap ve Pydantic ile doğrula[cite: 3]
        validated_data = StructuredOutputParser.parse(
            llm_output=raw_llm_output,
            schema=IdeaGenerationResponse
        )

        # Frontend'in veya Kişi 3'ün kullanabileceği dict formatında döndür
        return validated_data.model_dump()