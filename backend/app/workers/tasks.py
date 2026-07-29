"""Celery application instance and configuration."""

import os
from celery import Celery

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery_app = Celery(
    "sprintmate",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.workers.document_analysis_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Istanbul",
    enable_utc=True,
    task_track_started=True,
    worker_pool_restarts=True,
    # Celery/Kombu'ya varsayılan redis transport seçeneğinde RESP2 dayatıyoruz:
    broker_transport_options={
        "hostname": "localhost",
        "port": 6379,
        "protocol_version": 2,
    },
    result_backend_transport_options={
        "hostname": "localhost",
        "port": 6379,
        "protocol_version": 2,
    },
)