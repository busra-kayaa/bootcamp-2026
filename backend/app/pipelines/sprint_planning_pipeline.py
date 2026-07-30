from typing import List
from pydantic import BaseModel, Field
from app.infrastructure.llm.llm_provider import GroqLLMProvider
from app.infrastructure.llm.structured_output_parser import StructuredOutputParser

# Petek'in yazdığı prompt dosyasını import ediyoruz
from app.prompts.sprint_planner_prompt import SPRINT_PLANNER_PROMPT

# ---------------------------------------------------------
# Çıktı Formatını Zorlamak İçin Pydantic Şemaları
# ---------------------------------------------------------
class SprintTaskSchema(BaseModel):
    title: str = Field(description="Görev başlığı")
    responsible_role: str = Field(description="Görevi yapacak rol (Örn: Veri Mühendisi)")
    priority: str = Field(description="Yüksek, Orta veya Düşük")
    dependencies: List[str] = Field(default=[], description="Bu görevin bağlı olduğu diğer görevler")

class SprintSchema(BaseModel):
    sprint_no: int = Field(description="Sprint numarası")
    goal: str = Field(description="Bu sprintin ana hedefi")
    tasks: List[SprintTaskSchema] = Field(description="Sprint içindeki görevler")

class SprintPlanningResponse(BaseModel):
    sprints: List[SprintSchema]

# ---------------------------------------------------------
# Ana Pipeline Sınıfı
# ---------------------------------------------------------
class SprintPlanningPipeline:
    def __init__(self, llm_provider: GroqLLMProvider):
        # Sprint planlamada PDF'den RAG (arama) yapmaya çok gerek yoktur,
        # çünkü elimizde zaten projenin fikri ve şartname özeti var.
        self.llm_provider = llm_provider

    async def execute(self, idea_details: dict, team_size: int, sprint_count: int, rules_and_summary: str) -> dict:
        """
        Seçilen proje fikrini istenen sprint sayısına böler ve görevleri dağıtır.
        """
        
        # LLM'e gidecek bağlamı oluştur
        user_prompt = f"""
        Şartname Kuralları ve Özeti:
        {rules_and_summary}

        Seçilen Proje Fikri:
        Adı: {idea_details.get('name')}
        Açıklama: {idea_details.get('description')}

        Takım Büyüklüğü: {team_size} kişi
        İstenen Sprint Sayısı: {sprint_count}

        Lütfen bu projeyi {sprint_count} sprint'e böl ve {team_size} kişilik bir ekibe uygun görev dağılımını yap.
        """

        # Groq LLM'i JSON formatında çağır
        raw_llm_output = await self.llm_provider.generate_structured(
            system_prompt=SPRINT_PLANNER_PROMPT,
            user_prompt=user_prompt,
            response_schema=SprintPlanningResponse
        )

        # Çıktıyı parse et ve Pydantic ile doğrula
        validated_data = StructuredOutputParser.parse(
            llm_output=raw_llm_output,
            schema=SprintPlanningResponse
        )

        return validated_data.model_dump()