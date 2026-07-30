from app.pipelines.requirement_analysis_pipeline import RequirementAnalysisPipeline
from app.pipelines.idea_generation_pipeline import IdeaGenerationPipeline
from app.pipelines.sprint_planning_pipeline import SprintPlanningPipeline

class AnalysisService:
    def __init__(
        self,
        requirement_pipeline: RequirementAnalysisPipeline,
        idea_pipeline: IdeaGenerationPipeline,
        sprint_pipeline: SprintPlanningPipeline
    ):
        self.requirement_pipeline = requirement_pipeline
        self.idea_pipeline = idea_pipeline
        self.sprint_pipeline = sprint_pipeline

    async def analyze_document(self, document_id: int) -> dict:
        """
        Bir şartname dokümanı için tüm analiz ve fikir üretme süreçlerini sırayla koordine eder[cite: 3].
        """
        
        # 1. Şartname Analizi (Kurallar, Tarihler, Riskler)
        req_analysis = await self.requirement_pipeline.execute(document_id=document_id)
        
        # 2. Proje Fikri Üretimi için 1. adımdan çıkan özeti birleştir
        rules_summary_text = f"Özet: {req_analysis['summary']}\nKurallar: {req_analysis['rules']}"
        
        ideas = await self.idea_pipeline.execute(
            document_id=document_id,
            rules_and_summary=rules_summary_text
        )
        
        # 3. Sonuçları Kişi 3'ün API üzerinden döneceği tek bir JSON (Sözleşme) yapısında birleştir[cite: 3]
        return {
            "summary": req_analysis["summary"],
            "criticalDates": req_analysis["criticalDates"],
            "rules": req_analysis["rules"],
            "risks": req_analysis["risks"],
            "ideas": ideas["ideas"]
        }
        
    async def generate_sprint_plan(self, idea_details: dict, team_size: int, sprint_count: int, rules_and_summary: str) -> dict:
        """
        Kullanıcı bir fikir seçtiğinde çalışacak sprint planlama koordinatörü.
        """
        sprint_plan = await self.sprint_pipeline.execute(
            idea_details=idea_details,
            team_size=team_size,
            sprint_count=sprint_count,
            rules_and_summary=rules_and_summary
        )
        return sprint_plan