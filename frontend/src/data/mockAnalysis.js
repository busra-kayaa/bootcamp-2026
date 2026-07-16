export const mockAnalysis = {
  summary:
    "Yüklenen şartname; yenilikçi, uygulanabilir ve yapay zekâ katkısı net biçimde gösterilebilen projeleri önceliklendirmektedir. Takımların çalışan bir MVP, açık görev dağılımı ve ölçülebilir proje çıktıları sunması beklenmektedir.",

  criticalDates: [
    {
      title: "Sprint 2 Teslimi",
      date: "19 Temmuz 2026",
    },
    {
      title: "Proje Finali",
      date: "2 Ağustos 2026",
    },
    {
      title: "Top 10 Sunumu",
      date: "14 Ağustos 2026",
    },
  ],

  rules: [
    "Çalışan bir MVP hazırlanmalıdır.",
    "Yapay zekâ katkısı açık şekilde belirtilmelidir.",
    "Sprint Review ve Retrospective belgelenmelidir.",
    "Takım üyelerinin görev dağılımları gösterilmelidir.",
  ],

  ideas: [
    {
      title: "SprintMate AI",
      score: 94,
      description:
        "Şartnameleri analiz ederek proje fikri, backlog, risk analizi ve sprint planı oluşturan yapay zekâ asistanı.",
      aiContribution: "Yüksek",
    },
    {
      title: "TeamScope",
      score: 86,
      description:
        "Takım becerilerini analiz ederek görevleri otomatik biçimde ekip üyelerine dağıtan proje yönetim aracı.",
      aiContribution: "Orta-Yüksek",
    },
    {
      title: "DemoPilot",
      score: 81,
      description:
        "Proje özelliklerine göre sunum akışı ve jüri demo senaryosu oluşturan dijital asistan.",
      aiContribution: "Orta",
    },
  ],

  risks: [
    {
      title: "Kapsam büyümesi",
      description: "Final tarihine kadar gereğinden fazla özellik geliştirilmesi.",
      level: "Yüksek",
    },
    {
      title: "LLM gecikmesi",
      description: "Uzun dokümanlarda analiz süresinin yükselmesi.",
      level: "Orta",
    },
    {
      title: "Kaynak doğruluğu",
      description: "Üretilen bilginin şartnamedeki kaynakla eşleşmemesi.",
      level: "Orta",
    },
  ],
};