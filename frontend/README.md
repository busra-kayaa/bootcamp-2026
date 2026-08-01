# SprintMate AI – Frontend

SprintMate AI frontend uygulaması, kullanıcıların yarışma şartnamelerini yüklemesini, yapay zekâ tarafından oluşturulan analiz sonuçlarını gerçek zamanlı olarak görüntülemesini ve seçilen fikirler üzerinden proje sprint planlaması yapmasını sağlayan React tabanlı modern bir kullanıcı arayüzüdür.

## Kullanılan Teknolojiler

- React
- Vite
- JavaScript
- CSS
- Lucide React

## Mevcut Özellikler

- Modern ve responsive kullanıcı arayüzü
- PDF, TXT, DOC ve DOCX dosyası yükleme (Sürükle-bırak desteği)
- Şartname metnini doğrudan girebilme ve dosya formatı doğrulama
- FastAPI backend üzerinden gerçek zamanlı yapay zeka (LLM) analiz entegrasyonu
- Kritik tarihlerin, zorunlu kuralların ve genel özetin yapılandırılmış gösterimi
- Proje fikirlerinin AI katkısı ve uyum skoruyla listelenmesi
- Risk analizi sonuçlarının gösterilmesi
- **Fikir Detay Ekranı (IdeaDetail):** Seçilen fikirler için özel sayfada detaylı inceleme, sprint planlaması ve backlog oluşturma altyapısı
- Mobil ve masaüstü cihazlarla uyumlu tasarım

## API Entegrasyonu (Güncellendi)

Proje mock (geçici) veri kullanımından tamamen çıkmış olup, gerçek **FastAPI backend** sistemiyle asenkron olarak entegre edilmiştir. Arayüzden atılan dosya/metin istekleri doğrudan `http://localhost:8000/api/v1/documents` uç noktasına (endpoint) gönderilmektedir. *(Eski `mockAnalysis.js` yapısı tamamen iptal edilmiştir.)*

## Proje Yapısı

```text
src/
├── components/
│   ├── Navbar.jsx
│   ├── UploadWorkspace.jsx
│   ├── ResultPanel.jsx
│   └── IdeaDetail.jsx
├── App.jsx
├── App.css
├── index.css
└── main.jsx
```

## Projeyi Çalıştırma

Frontend klasörüne girin:

```bash
cd frontend
```

Gerekli paketleri yükleyin:

```bash
npm install
```

Geliştirme sunucusunu başlatın (NOT: İsteklerin çalışması için arka planda uvicorn backend'inin de çalışıyor olması gerekmektedir):

```bash
npm run dev
```

Terminalde gösterilen bağlantıyı tarayıcıda açın:

```text
http://localhost:5173
```

## Production Build

```bash
npm run build
```

## Veri Akışı

```text
Kullanıcı Doküman veya Metin Yükler
              ↓
Frontend Form Data API İsteği (POST /api/v1/documents)
              ↓
Backend NLP/LLM AI Doküman Analizi
              ↓
JSON Formatında Yapılandırılmış Analiz Sonuçlarının Dönmesi
              ↓
React State'e Kaydedilip Ekrana (ResultPanel & IdeaDetail) Çizilmesi
```

## Takım

Bu proje, Yapay Zekâ ve Teknoloji Akademisi Bootcamp süreci kapsamında Grup 57 tarafından geliştirilmektedir.