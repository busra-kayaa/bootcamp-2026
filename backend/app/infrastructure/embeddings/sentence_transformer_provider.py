import asyncio
from sentence_transformers import SentenceTransformer
from app.domain.interfaces.embedding_provider_interface import EmbeddingProviderInterface

class SentenceTransformerProvider(EmbeddingProviderInterface):
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        # Model sınıf çağrıldığında hafızaya bir kez yüklenir.
        self.model = SentenceTransformer(model_name)

    async def embed_text(self, text: str) -> list[float]:
        # Boş metin kontrolü
        if not text or not text.strip():
            return []
            
        # FastAPI'nin asenkron yapısını bloklamamak için işlemi to_thread ile arka planda çalıştırıyoruz
        embedding = await asyncio.to_thread(self.model.encode, text)
        return embedding.tolist()

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Boş liste kontrolü
        if not texts:
            return []
            
        # Birden fazla chunk'ı batch (toplu) olarak tek seferde vektöre çeviriyoruz
        embeddings = await asyncio.to_thread(self.model.encode, texts)
        return embeddings.tolist()