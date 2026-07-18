# SprintMate AI – Frontend

SprintMate AI frontend uygulaması, kullanıcıların yarışma şartnamelerini yüklemesini ve yapay zekâ tarafından oluşturulan analiz sonuçlarını görüntülemesini sağlayan React tabanlı kullanıcı arayüzüdür.

## Kullanılan Teknolojiler

- React
- Vite
- JavaScript
- CSS
- Lucide React

## Mevcut Özellikler

- Modern ve responsive kullanıcı arayüzü
- PDF, TXT, DOC ve DOCX dosyası yükleme
- Sürükle-bırak dosya yükleme desteği
- Şartname metnini doğrudan girme
- Dosya formatı doğrulama
- Analiz sırasında yükleniyor göstergesi
- Kritik tarihlerin ve kuralların görüntülenmesi
- Proje fikirlerinin listelenmesi
- Risk analizi sonuçlarının gösterilmesi
- Mobil ve masaüstü cihazlarla uyumlu tasarım

## Geçici Veri Kullanımı

Backend ve yapay zekâ entegrasyonu geliştirme aşamasında olduğu için analiz sonuçları şu anda örnek veriler kullanılarak gösterilmektedir.

Örnek veriler şu dosyada bulunmaktadır:

```text
src/data/mockAnalysis.js
```

Backend entegrasyonu tamamlandığında geçici veriler gerçek API sonuçlarıyla değiştirilecektir.

## Proje Yapısı

```text
src/
├── components/
│   ├── Navbar.jsx
│   ├── UploadWorkspace.jsx
│   └── ResultPanel.jsx
├── data/
│   └── mockAnalysis.js
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

Geliştirme sunucusunu başlatın:

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

## Planlanan Backend Akışı

```text
Doküman yükleme
      ↓
Frontend API isteği
      ↓
Backend doküman analizi
      ↓
Yapılandırılmış JSON sonucu
      ↓
Sonuçların arayüzde gösterilmesi
```

## Takım

Bu proje, Yapay Zekâ ve Teknoloji Akademisi Bootcamp süreci kapsamında Grup 57 tarafından geliştirilmektedir.