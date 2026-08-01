import { useEffect, useState } from 'react';

function IdeaDetail({ idea, documentId, onBack }) {
  const [sprintPlan, setSprintPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // documentId veya idea yoksa istek atma
    if (!idea || !documentId) return;

    const fetchSprintPlan = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/api/v1/documents/${documentId}/sprint-plan`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: idea.title,
            description: idea.description,
            aiContribution: idea.aiContribution || "Yapay zeka analiz ve önerisi"
          }),
        });

        if (!response.ok) throw new Error("Sprint planı oluşturulurken bir hata meydana geldi.");
        
        const data = await response.json();
        setSprintPlan(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSprintPlan();
  }, [idea, documentId]);

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
             <span className="card-label">YOL HARİTASI</span>
             <h3 style={{ marginTop: '24px' }}>Sprint Planlaması</h3>
             
             {isLoading && (
               <div style={{ padding: '40px 0', textAlign: 'center', color: '#8191ff' }}>
                 Yapay zekâ 5 kişilik takım için backlog ve sprint döngülerini kurguluyor. Lütfen bekleyin...
               </div>
             )}

             {error && (
               <div style={{ color: '#ff9ba8', marginTop: '20px', padding: '15px', background: 'rgba(255, 91, 112, 0.08)', borderRadius: '8px' }}>
                 {error}
               </div>
             )}

             {sprintPlan && !isLoading && (
               <div style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                 {sprintPlan.sprints.map((sprint, idx) => (
                   <div key={idx} style={{ background: 'rgba(10, 23, 39, 0.4)', padding: '24px', borderRadius: '16px', border: '1px solid rgba(129, 148, 178, 0.15)' }}>
                     <h4 style={{ margin: '0 0 8px 0', color: '#e1e9f4', fontSize: '18px' }}>{sprint.sprintName}</h4>
                     <p style={{ fontSize: '13px', color: '#8496ab', marginBottom: '20px', lineHeight: '1.6' }}><strong>Hedef:</strong> {sprint.goal}</p>
                     
                     <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '16px' }}>
                       {sprint.userStories.map((story, sIdx) => (
                         <li key={sIdx} style={{ fontSize: '13px', color: '#b8c6d7', background: 'rgba(6, 17, 30, 0.5)', border: '1px solid rgba(126, 146, 177, 0.1)', padding: '16px', borderRadius: '12px' }}>
                           <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                             <strong style={{ color: '#cfdae8', lineHeight: '1.4' }}>{story.title}</strong>
                             <span style={{ color: '#65cba3', fontWeight: 'bold', background: 'rgba(74, 203, 150, 0.06)', border: '1px solid rgba(74, 203, 150, 0.15)', padding: '4px 8px', borderRadius: '6px', fontSize: '11px', whiteSpace: 'nowrap', marginLeft: '12px' }}>
                               {story.storyPoints} SP
                             </span>
                           </div>
                           
                           <ul style={{ margin: '0', padding: '0', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                             {story.tasks.map((task, tIdx) => (
                               <li key={tIdx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(11, 25, 42, 0.6)', padding: '10px 12px', borderRadius: '8px', fontSize: '12px' }}>
                                 <span style={{ color: '#9eafc3' }}>• {task.title}</span>
                                 <div style={{ display: 'flex', gap: '8px' }}>
                                   <span style={{ color: '#566a81', fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{task.priority}</span>
                                   <span style={{ color: '#7889ff', fontSize: '10px', background: 'rgba(118, 103, 255, 0.1)', padding: '2px 6px', borderRadius: '4px' }}>{task.responsible_role}</span>
                                 </div>
                               </li>
                             ))}
                           </ul>
                         </li>
                       ))}
                     </ul>
                   </div>
                 ))}
               </div>
             )}
          </article>
        </div>
      </section>
    </main>
  );
}

export default IdeaDetail;