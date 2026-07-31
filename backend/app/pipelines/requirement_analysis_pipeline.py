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
# Çıktı Formatını Zorlamak İçin Pydantic Şemaları
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

# --- YENİ EKLENEN FİKİR (IDEA) ŞEMASI ---
class IdeaSchema(BaseModel):
    title: str = Field(description="Proje fikrinin başlığı")
    description: str = Field(description="Fikrin detayı ve şartnameye nasıl tam uyum sağladığı")
    score: int = Field(description="Bu fikrin şartname hedefleriyle uyum puanı (0-100 arası tam sayı)")
    aiContribution: str = Field(description="Yapay zekânın bu fikre katabileceği ekstra inovatif değer")

class RequirementAnalysisResponse(BaseModel):
    summary: str = Field(description="Şartnamenin genel özeti ve temel beklentileri")
    criticalDates: List[CriticalDateSchema]
    rules: List[RuleSchema]
    risks: List[RiskSchema]
    ideas: List[IdeaSchema] # 👈 Şemaya eklendi

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
        Şartnameyi analiz ederek özet, tarihler, kurallar, riskler ve proje önerilerini çıkarır.
        """
        
        # 1. RAG için arama sorgusunu vektöre çevir
        # Fikir üretebilmesi için vektör sorgusuna "proje hedefleri ve beklentiler" kelimelerini de ekledik.
        query = "Yarışmanın son başvuru tarihleri, takvim, zorunlu kurallar, yasaklar, takım kısıtlamaları, puanlama kriterleri, proje hedefleri, diskalifiye sebepleri, cezalar ve elenme riskleri nelerdir?"
        query_embedding = await self.embedding_provider.embed_text(query)

        # 2. Veritabanından (PGVector) şartnamenin kural ve tarihlerle ilgili kısımlarını getir
        relevant_chunks = await self.vector_store.similarity_search(
            document_id=document_id,
            query_embedding=query_embedding,
            top_k=10  # Analiz için biraz daha geniş bir bağlam (10 chunk) çekiyoruz
        )

        # 3. LLM için bağlamı kaynak ID'leri ve sayfa numaralarıyla hazırla
        context_text = "\n\n".join(
            [f"[Kaynak ID: {c['chunk_id']}] Sayfa {c['page_start']}: {c['text']}" for c in relevant_chunks]
        )

        user_prompt = f"""
        Şartnameden Çekilen İlgili Bölümler (RAG Bağlamı):
        {context_text}

        Lütfen yukarıdaki bağlamı kullanarak şartnameyi analiz et. Tarihleri, kuralları, riskleri çıkar ve bunlara uygun yenilikçi proje önerileri üret.
        
        ÖNEMLİ ANALİZ KURALLARI:
        1. TARİHLER: Tarihler bir başlangıç ve bitiş aralığı içeriyorsa (Örn: 19 Haziran - 5 Temmuz), tarihi kesinlikle kırpma ve aralığın tamamını al.
        2. RİSKLER: Riskleri analiz ederken özellikle 'diskalifiye sebebi', 'yasak' veya 'elenme' gibi doğrudan projeyi başarısız kılacak kritik kuralları kesinlikle YÜKSEK öncelikli risk olarak belirle.
        3. KAYNAK GÖSTERİMİ: Kurallar, tarihler ve riskler için bulduğun her bilginin yanına mutlaka '[Kaynak ID: ...]' formatındaki chunk ID'sini ve sayfa numarasını ekle. Metinde yoksa asla uydurma.
        4. FİKİRLER (IDEAS): Proje önerileri (ideas) tamamen senin mühendislik vizyonun ve sentezin olacağı için, fikirlerin açıklamasına (description) KESİNLİKLE sayfa numarası veya kaynak ID ekleme.
        """

        # 5. Groq LLM'i JSON formatında cevap üretmeye zorlayarak çağır
        raw_llm_output = await self.llm_provider.generate_structured(
            system_prompt=REQUIREMENT_AGENT_PROMPT,
            user_prompt=user_prompt,
            response_schema=RequirementAnalysisResponse
        )

        # 6. Çıktıyı parse et ve Pydantic ile doğrula
        validated_data = StructuredOutputParser.parse(
            llm_output=raw_llm_output,
            schema=RequirementAnalysisResponse
        )

        return validated_data.model_dump()