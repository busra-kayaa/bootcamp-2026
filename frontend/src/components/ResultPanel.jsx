function ResultPanel({ result }) {
  return (
    <section className="results-section" id="results">
      <div className="results-heading">
        <div>
          <span className="section-label">ANALİZ TAMAMLANDI</span>
          <h2>Şartname analiz sonuçları</h2>
          <p>
            Kritik bilgiler, proje önerileri ve riskler yapay zekâ tarafından
            yapılandırıldı.
          </p>
        </div>

        <span className="source-chip">{result.sourceName}</span>
      </div>

      <div className="results-grid">
        <article className="result-card result-card--summary">
          <span className="card-number">01</span>
          <span className="card-label">GENEL ÖZET</span>
          <h3>Şartnamenin temel beklentileri</h3>
          <p>{result.summary}</p>

          <div className="source-reference">
            Kaynak: Yüklenen dokümanın analiz edilen bölümleri
          </div>
        </article>

        <article className="result-card">
          <span className="card-number">02</span>
          <span className="card-label">KRİTİK TARİHLER</span>

          <div className="date-list">
            {result.criticalDates.map((item) => (
              <div className="date-item" key={item.title}>
                <span />
                <div>
                  <strong>{item.title}</strong>
                  <small>{item.date}</small>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="result-card">
          <span className="card-number">03</span>
          <span className="card-label">ZORUNLU KURALLAR</span>

          <ul className="rule-list">
            {result.rules.map((rule) => (
              <li key={rule}>
                <span>✓</span>
                {rule}
              </li>
            ))}
          </ul>
        </article>
      </div>

      <div className="content-heading">
        <div>
          <span className="section-label">PROJE ÖNERİLERİ</span>
          <h3>Şartnameye en uygun fikirler</h3>
        </div>

        <span>{result.ideas.length} öneri bulundu</span>
      </div>

      <div className="idea-grid">
        {result.ideas.map((idea, index) => (
          <article className="idea-card" key={idea.title}>
            <div className="idea-card-header">
              <span className="idea-index">
                {String(index + 1).padStart(2, "0")}
              </span>

              <span className="score-badge">%{idea.score} uyum</span>
            </div>

            <h3>{idea.title}</h3>
            <p>{idea.description}</p>

            <div className="idea-meta">
              <span>AI katkısı</span>
              <strong>{idea.aiContribution}</strong>
            </div>

            <button type="button">Bu fikri seç</button>
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
        {result.risks.map((risk) => (
          <article className="risk-item" key={risk.title}>
            <div>
              <strong>{risk.title}</strong>
              <p>{risk.description}</p>
            </div>

            <span
              className={`risk-level risk-level--${risk.level
                .toLocaleLowerCase("tr-TR")
                .replace("ü", "u")}`}
            >
              {risk.level}
            </span>
          </article>
        ))}
      </div>
    </section>
  );
}

export default ResultPanel;