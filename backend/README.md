# Bootcamp AI Backend

## Kurulum ve çalıştırma

Backend klasöründe Windows PowerShell ile aşağıdaki komutları çalıştırın:

```powershell
python -m venv .venv
.\.venv\Scripts\activate  
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```
# Redis & Celery Arka Plan Görev Yöneticisi Kurulumu

Projeye eklenen asenkron doküman analiz boru hattı  için yerelde **Redis** ve **Celery** servislerinin çalışıyor olması gerekmektedir. 

* **Redis Sunucusu:** Yerel bilgisayarınızda Redis sunucusunun (`redis-server.exe`) `6379` portunda çalıştığından emin olmak için terminalde `redis-cli ping` komutunu çalıştırabilirsiniz (Ekrana `PONG` yanıtı geliyorsa Redis sunucunuz hazırdır). 

* **Bağımlılıklar:** Eski Windows Redis sürümleriyle yaşanan protokol uyumsuzluklarını (`unknown command HELLO`) önlemek amacıyla özel paket kısıtlamaları eklendiğinden, sanal ortamınızda `pip install -r requirements.txt` komutuyla paketleri güncelleyin. 

* **Worker'ı Başlatma:** `backend` klasöründe sanal ortamınız aktifken
 `python -m celery -A app.workers.tasks.celery_app worker --loglevel=info -P threads` komutunu çalıştırın.
 
  Terminalde `[tasks] . analyze_document_task`, `Connected to redis://localhost:6379/0` ve `celery@... ready.` satırlarını gördüğünüzde Celery çalışmaya başlar. 

Health endpoint: http://127.0.0.1:8000/health

Swagger arayüzü: http://127.0.0.1:8000/docs

Testleri çalıştırmak için:

```powershell
pytest
```
