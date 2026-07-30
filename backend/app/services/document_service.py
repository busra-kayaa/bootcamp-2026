import os
import uuid
import tempfile
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

# Kendi modellerinizi import ettiğiniz yer (Proje yapınıza göre güncelleyebilirsiniz)
from app.models import Document, DocumentChunk

from app.pipelines.requirement_analysis_pipeline import RequirementAnalysisPipeline
from app.infrastructure.vector_store.pgvector_store import PGVectorStore
from app.infrastructure.llm.llm_provider import GroqLLMProvider
from app.infrastructure.embeddings.sentence_transformer_provider import SentenceTransformerProvider

from app.infrastructure.pdf.pdfplumber_extractor import PdfPlumberExtractor

class DocumentService:
    def __init__(self, db: AsyncSession = None):
        self.db = db
        
        self.vector_store = PGVectorStore(db_session=self.db) 
        self.llm_provider = GroqLLMProvider()
        self.embedding_provider = SentenceTransformerProvider()
        
        self.pipeline = RequirementAnalysisPipeline(
            vector_store=self.vector_store,
            llm_provider=self.llm_provider,
            embedding_provider=self.embedding_provider
        )

    async def process_upload(self, file=None, text=None):
        filename = file.filename if file else "Yüklenen_Sartname.pdf"
        
        try:
            # ---------------------------------------------------------
            # 1. ADIM: DOKÜMANI VERİTABANINA KAYDET
            # ---------------------------------------------------------
            new_document = Document(
                filename=filename,
                file_hash=uuid.uuid4().hex,
                file_path=f"/temp/{filename}",
                mime_type=file.content_type if file else "application/pdf",
                processing_status='IN_PROGRESS',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(new_document)
            await self.db.flush() # Veritabanına yazmadan ID'yi almak için flush
            
            actual_document_id = new_document.id

            # ---------------------------------------------------------
            # 2. ADIM: PDF'İ OKU VE METNİ ÇIKAR (SENİN KODUNLA)
            # ---------------------------------------------------------
            extracted_pages = []
            
            if file:
                # PDF çıkarıcın bir dosya yolu (path) beklediği için geçici dosya (temp) oluşturuyoruz
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    content = await file.read()
                    tmp.write(content)
                    tmp_path = tmp.name

                try:
                    # Hazırladığın çıkarıcıyı ayağa kaldır ve metni çek
                    extractor = PdfPlumberExtractor()
                    extracted_pages = extractor.extract(tmp_path)
                finally:
                    # İşlem bitince veya hata çıkarsa geçici dosyayı sunucudan temizle
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
            else:
                # Sadece düz metin gönderildiyse manuel sayfa yarat
                extracted_pages = [{"page_number": 1, "text": text or "", "extraction_method": "manual"}]

            # ---------------------------------------------------------
            # 3. ADIM: CHUNKING VE VEKTÖR (EMBEDDING) OLUŞTURMA
            # ---------------------------------------------------------
            chunk_size = 1000
            chunk_index = 0
            
            # Senin sınıfından gelen sayfa sayfa verileri döngüye alıyoruz
            for page in extracted_pages:
                page_text = page["text"]
                page_num = page["page_number"] # PDF'teki gerçek sayfa numarasını yakaladık!
                
                if not page_text.strip():
                    continue
                    
                # Her bir sayfanın metnini chunk'lara bölüyoruz
                page_chunks = [page_text[i:i+chunk_size] for i in range(0, len(page_text), chunk_size)]
                
                for chunk_text in page_chunks:
                    if not chunk_text.strip():
                        continue
                        
                    # Vektör dönüşümü
                    embedding_vector = await self.embedding_provider.embed_text(chunk_text)
                    
                    new_chunk = DocumentChunk(
                        document_id=actual_document_id,
                        chunk_id=str(uuid.uuid4()),
                        chunk_index=chunk_index,
                        text=chunk_text,
                        page_start=page_num, # Frontend'de tıkladığında doğru sayfayı gösterecek
                        page_end=page_num,
                        embedding=embedding_vector,
                        created_at=datetime.utcnow()
                    )
                    self.db.add(new_chunk)
                    chunk_index += 1

            # Vektörleri ve parçaları güvenle veritabanına kaydet
            await self.db.commit()

            # ---------------------------------------------------------
            # 4. ADIM: YAPAY ZEKA ANALİZİ (Pipeline)
            # ---------------------------------------------------------
            ai_result = await self.pipeline.execute(document_id=actual_document_id)

            if not ai_result:
                raise ValueError("Pipeline boş sonuç döndürdü")

            # Dokümanın statüsünü tamamlandı olarak güncelle
            new_document.processing_status = 'SUCCESS'
            new_document.updated_at = datetime.utcnow()
            await self.db.commit()

            return {
                "message": "Şartname yapay zekâ tarafından başarıyla analiz edildi",
                "sourceName": filename,
                "summary": ai_result.get("summary", ""),
                "criticalDates": ai_result.get("criticalDates", []),
                "rules": ai_result.get("rules", []),
                "ideas": [],
                "risks": ai_result.get("risks", [])
            }

        except Exception as e:
            await self.db.rollback()
            print(f"Gerçek LLM Analiz Hatası: {e}")
            raise e