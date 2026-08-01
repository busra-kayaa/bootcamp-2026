import { useEffect, useState } from "react";

function ResultPanel({ result, onIdeaSelect }) {
  // Fikirleri lokal state'e alıyoruz. Yenileme yapıldığında sadece bu kısım güncellenecek.
  const [currentIdeas, setCurrentIdeas] = useState(result?.ideas || []);
  const [isRegenerating, setIsRegenerating] = useState(false);

  // Ana analiz sonucu (result) dışarıdan değişirse lokal state'i senkronize et
  useEffect(() => {
    if (result?.ideas) {
      setCurrentIdeas(result.ideas);
    }
  }, [result]);

  const handleRegenerate = async () => {
    if (!result?.documentId) {
      alert("Doküman ID bulunamadı, işlem yapılamaz.");
      return;
    }

    setIsRegenerating(true);
    try {
      // Birazdan backend'de oluşturacağımız yeni uç noktaya istek atıyoruz
      const response = await fetch(`http://localhost:8000/api/v1/documents/${result.documentId}/regenerate-ideas`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error("Fikirler üretilirken bir hata oluştu.");
      
      const data = await response.json();
      
      // Sadece fikirler state'ini yeni gelen 3 fikirle güncelliyoruz
      setCurrentIdeas(data.ideas);
    } catch (error) {
      console.error("Yenileme hatası:", error);
      alert("Yeni fikirler üretilemedi. Sunucu bağlantısını kontrol edin.");
    } finally {
      setIsRegenerating(false);
    }
  };

  if (!result) return null;

  return (
    <section className="results-section" id="results">
      <div className="results-heading">
        <div>
          <span className="section-label">ANALİZ TAMAMLANDI</span>
          <h2>Şartname analiz sonuçları</h2>
          <p>
            Kritik bilgiler, proje önerileri ve riskler yapay zekâ tarafından yapılandırıldı.
          </p>
        </div>
        <span className="source-chip">{result?.sourceName || "Yüklenen Şartname"}</span>
      </div>

      <div className="results-grid">
        <article className="result-card result-card--summary">
          <span className="card-number">01</span>
          <span className="card-label">GENEL ÖZET</span>
          <h3>Şartnamenin temel beklentileri</h3>
          <p>{result?.summary || "Özet bulunamadı."}</p>
          <div className="source-reference">
            Kaynak: Yüklenen dokümanın analiz edilen bölümleri
          </div>
        </article>

        <article className="result-card">
          <span className="card-number">02</span>
          <span className="card-label">KRİTİK TARİHLER</span>
          <div className="date-list">
            {(result?.criticalDates || []).map((item, idx) => (
              <div className="date-item" key={item?.title || idx}>
                <span />
                <div>
                  <strong>{item?.title}</strong>
                  <small>{item?.date}</small>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="result-card">
          <span className="card-number">03</span>
          <span className="card-label">ZORUNLU KURALLAR</span>
          <ul className="rule-list">
            {(result?.rules || []).map((rule, idx) => (
              <li key={idx}>
                <span>✓</span>
                <div>
                  <strong>[{rule?.category}]</strong> {rule?.text}
                  {rule?.risk_level && <small> ({rule.risk_level})</small>}
                </div>
              </li>
            ))}
          </ul>
        </article>
      </div>

      <div className="content-heading" style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <span className="section-label">PROJE ÖNERİLERİ</span>
          <h3>Şartnameye en uygun fikirler</h3>
        </div>

        {/* YENİ EKLENEN BUTON VE SAYAÇ ALANI */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ color: '#8496ab', fontSize: '13px' }}>{currentIdeas.length} öneri bulundu</span>
          
          <button 
            onClick={handleRegenerate}
            disabled={isRegenerating}
            style={{
              background: isRegenerating ? 'rgba(118, 103, 255, 0.05)' : 'rgba(118, 103, 255, 0.1)',
              border: '1px solid rgba(118, 103, 255, 0.3)',
              color: isRegenerating ? '#566a81' : '#8191ff',
              padding: '8px 16px',
              borderRadius: '8px',
              cursor: isRegenerating ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '13px',
              fontWeight: '600',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => !isRegenerating && (e.currentTarget.style.background = 'rgba(118, 103, 255, 0.2)')}
            onMouseOut={(e) => !isRegenerating && (e.currentTarget.style.background = 'rgba(118, 103, 255, 0.1)')}
          >
            {isRegenerating ? "🔄 Yapay zekâ düşünüyor..." : "🔄 Başka Fikirler Üret"}
          </button>
        </div>
      </div>

      {/* Yükleme sırasında kartların soluklaşması için dinamik stil eklendi */}
      <div className="idea-grid" style={{ opacity: isRegenerating ? 0.4 : 1, pointerEvents: isRegenerating ? 'none' : 'auto', transition: 'opacity 0.3s' }}>
        {currentIdeas.map((idea, index) => (
          <article className="idea-card" key={idea?.title || index}>
            <div className="idea-card-header">
              <span className="idea-index">
                {String(index + 1).padStart(2, "0")}
              </span>
              <span className="score-badge">%{idea?.score || 0} uyum</span>
            </div>
            <h3>{idea?.title}</h3>
            <p>{idea?.description}</p>
            <div className="idea-meta">
              <span className="ai-label">AI Katkısı</span>
              {idea.aiContribution}
            </div>
            <button type="button" onClick={() => onIdeaSelect && onIdeaSelect(idea)}>Bu fikri seç</button>
          </article>
        ))}
      </div>

      <div className="content-heading">
        <div>
          <span className="section-label">RİSK ANALİZİ</span>
          <h3>Önceden önlem alınması gereken noktalar</h3>
        </div>
      </div>

      <div className="risk-list">
        {(result?.risks || []).map((risk, idx) => (
          <article className="risk-item" key={risk?.title || idx}>
            <div>
              <strong>{risk?.title}</strong>
              <p>{risk?.description}</p>
            </div>
            <span
              className={`risk-level risk-level--${(risk?.level || "Orta")
                .toLocaleLowerCase("tr-TR")
                .replace("ü", "u")}`}
            >
              {risk?.level}
            </span>
          </article>
        ))}
      </div>
    </section>
  );
}

export default ResultPanel;