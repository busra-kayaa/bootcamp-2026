import { useState } from 'react';
import './App.css';

function App() {
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const formData = new FormData();
    if (text) formData.append('text_input', text);
    if (file) formData.append('file', file);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/analyze', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Bağlantı hatası:", error);
      alert("Backend'e ulaşılamadı. FastAPI sunucusunun açık olduğundan emin olun.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>SprintMate AI 🚀</h1>
        <p>Bootcamp & Hackathon Şartname Analiz Asistanı</p>
      </header>
      
      <main className="main-content">
        <form onSubmit={handleSubmit} className="upload-form">
          <div className="input-group">
            <label>Şartname Metnini Yapıştırın</label>
            <textarea 
              rows="8" 
              placeholder="Şartname kurallarını buraya yapıştırın..." 
              value={text} 
              onChange={(e) => setText(e.target.value)}
            />
          </div>
          
          <div className="divider">VEYA</div>

          <div className="input-group file-drop-area">
            <label htmlFor="file-upload" className="file-label">
              <span className="upload-icon">📄</span>
              <span>PDF Şartname Yükleyin</span>
            </label>
            <input 
              id="file-upload"
              type="file" 
              accept=".pdf" 
              onChange={(e) => setFile(e.target.files[0])}
            />
            {file && <p className="file-name">Seçilen dosya: {file.name}</p>}
          </div>
          
          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Analiz Ediliyor, Lütfen Bekleyin...' : 'Şartnameyi Analiz Et'}
          </button>
        </form>

        {result && (
          <div className="result-card">
            <h2>✅ Analiz Sonucu</h2>
            <div className="result-content">
              <p><strong>Durum:</strong> {result.status}</p>
              <p><strong>Arka Planda İşlenen Metin Önizlemesi:</strong></p>
              <blockquote>{result.preview}</blockquote>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;