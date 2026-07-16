import { useState } from "react";
import "./App.css";

import Navbar from "./components/Navbar";
import UploadWorkspace from "./components/UploadWorkspace";
import ResultPanel from "./components/ResultPanel";
import { mockAnalysis } from "./data/mockAnalysis";

const features = [
  {
    number: "01",
    title: "Kritik bilgi çıkarımı",
    description:
      "Teslim tarihleri, kurallar, yasaklar ve puanlama kriterleri otomatik olarak belirlenir.",
  },
  {
    number: "02",
    title: "Proje fikri üretimi",
    description:
      "Şartnameye uygun ve uygulanabilir proje fikirleri karşılaştırmalı olarak sunulur.",
  },
  {
    number: "03",
    title: "Sprint planlaması",
    description:
      "Seçilen fikir backlog, user story ve uygulanabilir sprint görevlerine dönüştürülür.",
  },
];

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleAnalyze = async ({ text, file }) => {
    setIsLoading(true);
    setAnalysisResult(null);

    // Backend hazır olmadığı için şimdilik yapay bekleme kullanıyoruz.
    await new Promise((resolve) => setTimeout(resolve, 1400));

    setAnalysisResult({
      ...mockAnalysis,
      sourceName: file?.name || "Girilen şartname metni",
      inputLength: text.length,
    });

    setIsLoading(false);

    setTimeout(() => {
      document.getElementById("results")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 100);
  };

  return (
    <div className="app-shell" id="top">
      <div className="background-grid" />
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <Navbar />

      <main>
        <section className="hero-section">
          <div className="hero-content">
            <span className="eyebrow">
              <span />
              Yapay zekâ destekli proje planlama
            </span>

            <h1>
              Uzun şartnameleri
              <span className="gradient-text"> uygulanabilir projelere </span>
              dönüştürün.
            </h1>

            <p className="hero-description">
              SprintMate AI; yarışma dokümanlarını analiz eder, kritik kuralları
              çıkarır ve takımınız için proje fikri, backlog, sprint planı ve
              risk analizi oluşturur.
            </p>

            <div className="hero-actions">
              <a className="primary-link" href="#workspace">
                Analize başla
                <span>→</span>
              </a>

              <a className="secondary-link" href="#features">
                Nasıl çalışır?
              </a>
            </div>

            <div className="hero-stats">
              <div>
                <strong>4+</strong>
                <span>Analiz modülü</span>
              </div>

              <div>
                <strong>3</strong>
                <span>Sprint planlaması</span>
              </div>

              <div>
                <strong>AI</strong>
                <span>Kaynaklı çıktılar</span>
              </div>
            </div>
          </div>

          <UploadWorkspace
            onAnalyze={handleAnalyze}
            isLoading={isLoading}
          />
        </section>

        <section className="features-section" id="features">
          <div className="section-heading">
            <span className="section-label">NASIL ÇALIŞIR?</span>
            <h2>Fikir aşamasından sprint planına kadar tek çalışma alanı</h2>
            <p>
              Takımınız doküman okumakla zaman kaybetmez, doğrudan uygulanabilir
              çıktılar üzerinden ilerler.
            </p>
          </div>

          <div className="feature-grid">
            {features.map((feature) => (
              <article className="feature-card" key={feature.number}>
                <span>{feature.number}</span>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </article>
            ))}
          </div>
        </section>

        {analysisResult && <ResultPanel result={analysisResult} />}
      </main>

      <footer>
        <div>
          <strong>SprintMate AI</strong>
          <span>Grup 57 · Yapay Zekâ ve Teknoloji Akademisi</span>
        </div>

        <span>Bootcamp MVP · 2026</span>
      </footer>
    </div>
  );
}

export default App;