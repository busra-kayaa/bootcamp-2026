# Bootcamp AI Backend

## Kurulum ve çalıştırma

Backend klasöründe Windows PowerShell ile aşağıdaki komutları çalıştırın:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Health endpoint: http://127.0.0.1:8000/health

Swagger arayüzü: http://127.0.0.1:8000/docs

Testleri çalıştırmak için:

```powershell
pytest
```
