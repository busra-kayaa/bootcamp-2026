import React from 'react';

function IdeaDetail({ idea, onBack }) {
  if (!idea) return null;

  return (
    <main className="idea-detail-page" style={{ minHeight: '80vh', padding: '40px 0' }}>
      <section className="results-section">
        <button 
          onClick={onBack}
          style={{
             background: 'rgba(17, 32, 51, 0.7)', 
             border: '1px solid rgba(129, 148, 178, 0.16)', 
             color: '#b8c6d7', 
             padding: '10px 20px', 
             borderRadius: '11px',
             cursor: 'pointer',
             marginBottom: '40px',
             fontSize: '13px',
             fontWeight: '600',
             display: 'flex',
             alignItems: 'center',
             gap: '8px',
             transition: 'transform 180ms ease, background 180ms ease'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = 'rgba(25, 45, 70, 0.9)';
            e.currentTarget.style.transform = 'translateY(-2px)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = 'rgba(17, 32, 51, 0.7)';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          <span>←</span> Geri Dön
        </button>

        <div className="results-heading">
          <div>
            <span className="section-label">SEÇİLEN FİKİR DETAYI</span>
            <h2>{idea.title}</h2>
            <p>Bu fikir için planlama, sprint ve detaylı açıklamalar aşağıdadır.</p>
          </div>
          <span className="score-badge" style={{ fontSize: '14px', padding: '10px 16px' }}>
            %{idea.score || 0} uyum
          </span>
        </div>

        <div className="results-grid" style={{ gridTemplateColumns: '1fr', gap: '24px' }}>
          <article className="result-card result-card--summary" style={{ minHeight: 'auto' }}>
            <span className="card-number">01</span>
            <span className="card-label">PROJE AÇIKLAMASI</span>
            <h3 style={{ marginTop: '24px' }}>Genel Bakış</h3>
            <p>{idea.description}</p>
            
            <div className="source-reference" style={{ marginTop: '20px', display: 'flex', alignItems: 'center', gap: '10px', fontSize: '12px' }}>
               <span style={{ color: '#8191ff', fontWeight: 'bold' }}>AI Katkısı:</span> 
               <span style={{ color: '#aebed0' }}>{idea.aiContribution || 'Yapay zeka analiz ve önerisi'}</span>
            </div>
          </article>
          
          <article className="result-card" style={{ minHeight: 'auto' }}>
             <span className="card-number">02</span>
             <span className="card-label">YOL HARİTASI (Yakında)</span>
             <h3 style={{ marginTop: '24px' }}>Sprint Planlaması</h3>
             <p style={{ marginBottom: '0' }}>
               Bu proje fikri için detaylı backlog ve sprint görevleri bu alanda listelenecektir. 
               Şu anda entegrasyon aşamasındadır.
             </p>
          </article>
        </div>
      </section>
    </main>
  );
}

export default IdeaDetail;
