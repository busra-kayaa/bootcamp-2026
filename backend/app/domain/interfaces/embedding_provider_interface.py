from abc import ABC, abstractmethod

class EmbeddingProviderInterface(ABC):
    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Tek bir metni vektöre çevirir."""
        pass

    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Birden fazla metni (chunk) toplu olarak vektöre çevirir."""
        pass