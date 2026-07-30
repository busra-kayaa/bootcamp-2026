import json
from typing import List, Optional
from pydantic import BaseModel, Field

# Altyapı sağlayıcıları
from app.infrastructure.vector_store.pgvector_store import PGVectorStore
from app.infrastructure.llm.llm_provider import GroqLLMProvider
from app.infrastructure.embeddings.sentence_transformer_provider import SentenceTransformerProvider
from app.infrastructure.llm.structured_output_parser import StructuredOutputParser

from app.prompts.requirement_prompts import REQUIREMENT_AGENT_PROMPT

# ---------------------------------------------------------
# Çıktı Formatını Zorlamak İçin Pydantic Şemaları[cite: 3]
# Frontend'in beklediği camelCase yapısına uygun hazırlanmıştır.
# ---------------------------------------------------------
class CriticalDateSchema(BaseModel):
    title: str = Field(description="Tarihin neye ait olduğu (Örn: Son başvuru tarihi)")
    date: str = Field(description="Tarih değeri")
    sourcePage: Optional[int] = Field(None, description="Bilginin geçtiği sayfa numarası")
    sourceChunkId: Optional[str] = Field(None, description="Kaynak chunk ID'si")

class RuleSchema(BaseModel):
    category: str = Field(description="Kuralın kategorisi (Örn: Zorunlu Kural, Yasak)")
    text: str = Field(description="Kuralın içeriği")
    risk_level: str = Field(description="Kritik, Orta veya Düşük")
    sourcePage: Optional[int] = None
    sourceChunkId: Optional[str] = None

class RiskSchema(BaseModel):
    title: str = Field(description="Riskin başlığı (Örn: Kapsam büyümesi)")
    description: str = Field(description="Riskin detayı")
    level: str = Field(description="YÜKSEK, ORTA veya DÜŞÜK")
    sourceChunkId: Optional[str] = None

class RequirementAnalysisResponse(BaseModel):
    summary: str = Field(description="Şartnamenin genel özeti ve temel beklentileri")
    criticalDates: List[CriticalDateSchema]
    rules: List[RuleSchema]
    risks: List[RiskSchema]

# ---------------------------------------------------------
# Ana Pipeline Sınıfı
# ---------------------------------------------------------
class RequirementAnalysisPipeline:
    def __init__(
        self,
        vector_store: PGVectorStore,
        llm_provider: GroqLLMProvider,
        embedding_provider: SentenceTransformerProvider
    ):
        self.vector_store = vector_store
        self.llm_provider = llm_provider
        self.embedding_provider = embedding_provider

    async def execute(self, document_id: int) -> dict:
        """
        Şartnameyi analiz ederek özet, tarihler, kurallar ve riskleri çıkarır[cite: 3].
        """
        
        # 1. RAG için arama sorgusunu vektöre çevir
        query = "Yarışmanın son başvuru tarihleri, takvim, zorunlu kurallar, yasaklar, takım kısıtlamaları ve puanlama kriterleri nelerdir?"
        query_embedding = await self.embedding_provider.embed_text(query)

        # 2. Veritabanından (PGVector) şartnamenin kural ve tarihlerle ilgili kısımlarını getir[cite: 3]
        relevant_chunks = await self.vector_store.similarity_search(
            document_id=document_id,
            query_embedding=query_embedding,
            top_k=10  # Analiz için biraz daha geniş bir bağlam (10 chunk) çekiyoruz
        )

        # 3. LLM için bağlamı kaynak ID'leri ve sayfa numaralarıyla hazırla[cite: 3]
        context_text = "\n\n".join(
            [f"[Kaynak ID: {c['chunk_id']}] Sayfa {c['page_start']}: {c['text']}" for c in relevant_chunks]
        )

        # 4. LLM'e gidecek kullanıcı mesajını oluştur
        user_prompt = f"""
        Şartnameden Çekilen İlgili Bölümler (RAG Bağlamı):
        {context_text}

        Lütfen yukarıdaki bağlamı kullanarak şartnameyi analiz et. Tarihleri, kuralları ve riskleri çıkar.
        Bulduğun her bilginin yanına mutlaka '[Kaynak ID: ...]' formatındaki chunk ID'sini ve sayfa numarasını ekle[cite: 3].
        Eğer bir bilgi bu metinlerde yoksa, asla uydurma (halüsinasyon yapma), boş bırak.
        """

        # 5. Groq LLM'i JSON formatında cevap üretmeye zorlayarak çağır[cite: 3]
        raw_llm_output = await self.llm_provider.generate_structured(
            system_prompt=REQUIREMENT_AGENT_PROMPT,
            user_prompt=user_prompt,
            response_schema=RequirementAnalysisResponse
        )

        # 6. Çıktıyı parse et ve Pydantic ile doğrula[cite: 3]
        validated_data = StructuredOutputParser.parse(
            llm_output=raw_llm_output,
            schema=RequirementAnalysisResponse
        )

        return validated_data.model_dump()