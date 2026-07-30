from abc import ABC, abstractmethod

class LLMProviderInterface(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        """Standart metin üretimi."""
        pass

    @abstractmethod
    async def generate_structured(self, system_prompt: str, user_prompt: str, response_schema: type):
        """Pydantic şemasına uygun JSON üretimi."""
        pass