from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import re
import pdfplumber

app = FastAPI()

# --- CORS AYARLARI (İletişim kilidini açan kısım) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Geliştirme ortamında tüm adreslere izin verir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def nlp_normalize(text: str) -> str:
    """LLM öncesi hibrit metin normalizasyon motoru"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
    return text.strip()

@app.post("/api/analyze")
async def analyze_document(
    text_input: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    extracted_text = ""
    
    # PDF okuma işlemi
    if file and file.filename.endswith('.pdf'):
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + " "
    # Metin okuma işlemi
    elif text_input:
        extracted_text = text_input
        
    if not extracted_text:
        return {"error": "Lütfen metin veya PDF sağlayın."}
        
    normalized_text = nlp_normalize(extracted_text)
    
    return {
        "status": "success",
        "preview": normalized_text[:200] + "..." # Sadece ilk 200 karakteri döndürüyoruz
    }