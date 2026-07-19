from .tasks import celery_app
# İhtiyaca göre document_analysis_tasks içindeki ana task fonksiyonları da buraya eklenebilir.

__all__ = ["celery_app"]