from typing import List
from pydantic import BaseModel, Field
from app.infrastructure.llm.llm_provider import GroqLLMProvider
from app.infrastructure.llm.structured_output_parser import StructuredOutputParser
from app.prompts.sprint_planner_prompt import SPRINT_PLANNER_PROMPT

# ---------------------------------------------------------
# Çıktı Formatını Zorlamak İçin Pydantic Şemaları
# ---------------------------------------------------------
class SprintTaskSchema(BaseModel):
    title: str = Field(description="Görev başlığı")
    responsible_role: str = Field(description="Görevi yapacak rol (Örn: Veri Mühendisi, Scrum Master)")
    priority: str = Field(description="Yüksek, Orta veya Düşük")
    dependencies: List[str] = Field(default=[], description="Bu görevin bağlı olduğu diğer görevler")

# Frontend'in beklediği User Story katmanı eklendi
class UserStorySchema(BaseModel):
    title: str = Field(description="Kullanıcı hikayesi")
    storyPoints: int = Field(description="Bu işin karmaşıklık puanı (Fibonacci serisi: 1, 2, 3, 5, 8)")
    tasks: List[SprintTaskSchema] = Field(description="Bu hikayeyi tamamlamak için yapılması gereken alt görevler")

class SprintSchema(BaseModel):
    sprintName: str = Field(description="Sprint adı ve numarası (Örn: Sprint 1)")
    goal: str = Field(description="Bu sprintin ana hedefi")
    userStories: List[UserStorySchema] = Field(description="Sprint içindeki kullanıcı hikayeleri")

class SprintPlanningResponse(BaseModel):
    sprints: List[SprintSchema]

# ---------------------------------------------------------
# Ana Pipeline Sınıfı
# ---------------------------------------------------------
class SprintPlanningPipeline:
    # Route'taki çağırma yapısını bozmamak için args/kwargs ile uyumluluk sağlandı
    def __init__(self, llm_provider: GroqLLMProvider, *args, **kwargs):
        self.llm_provider = llm_provider

    async def execute(self, document_id: int, selected_idea: dict) -> dict:
        """
        Seçilen proje fikrini KULLANICI AYARLARINA göre sprintlere böler ve görevleri dağıtır.
        """
        
        idea_name = selected_idea.get('title', 'Belirtilmemiş Fikir')
        idea_description = selected_idea.get('description', '')
        
        # Frontend'den gelen dinamik ayarları çekiyoruz (Yoksa varsayılanları kullan)
        team_size = selected_idea.get('teamSize', 5)
        sprint_count = selected_idea.get('sprintCount', 3)
        custom_roles = selected_idea.get('customRoles', 'Product Owner, Scrum Master, Developer')
        
        user_prompt = f"""
        Seçilen Proje Fikri:
        Adı: {idea_name}
        Açıklama: {idea_description}

        Takım Büyüklüğü: {team_size} kişi
        Takımdaki Roller: {custom_roles}
        İstenen Toplam Sprint Sayısı: {sprint_count}

        Lütfen bu projeyi tam olarak {sprint_count} sprint'e böl. 
        Görevi yapacak sorumlu rolleri belirlerken SADECE yukarıda belirtilen "{custom_roles}" rollerinden seçim yap. Başka rol uydurma.
        
        KRİTİK VE ZORUNLU KURAL: "{custom_roles}" listesindeki HER BİR ROL, İSTİSNASIZ OLARAK HER SPRINT'TE en az bir göreve sahip olmalıdır. Sadece 'Developer' veya teknik rollere görev atayıp diğerlerini asla boş bırakma. 
        Örneğin:
        - Product Owner rolü varsa; backlog önceliklendirme, kullanıcı test senaryolarını onaylama, vizyon toplantıları gibi görevler yaz.
        - Scrum Master rolü varsa; daily scrum yönetimi, teknik engellerin (blocker) kaldırılması, sprint retro'sunun yapılması gibi görevler yaz.
        
        Tüm rollerin, her sprint döngüsünde aktif olarak takımın bir parçası olmasını sağla!
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