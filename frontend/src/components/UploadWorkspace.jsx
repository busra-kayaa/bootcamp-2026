import { useRef, useState } from "react";

function UploadWorkspace({ onAnalyze, isLoading }) {
  const fileInputRef = useRef(null);

  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState("");

  const validateAndSetFile = (selectedFile) => {
    if (!selectedFile) {
      return;
    }

    const isAllowedFile = /\.(pdf|txt|doc|docx)$/i.test(selectedFile.name);

    if (!isAllowedFile) {
      setError("Lütfen PDF, TXT, DOC veya DOCX formatında bir dosya yükleyin.");
      setFile(null);
      return;
    }

    setError("");
    setFile(selectedFile);
  };

  const handleFileChange = (event) => {
    validateAndSetFile(event.target.files?.[0]);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);

    validateAndSetFile(event.dataTransfer.files?.[0]);
  };

  const handleAnalyze = () => {
    if (!text.trim() && !file) {
      setError("Analiz için bir doküman yükleyin veya şartname metni girin.");
      return;
    }

    setError("");
    onAnalyze({ text, file });
  };

  const removeFile = (event) => {
    event.stopPropagation();

    setFile(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <section className="workspace-card" id="workspace">
      <div className="workspace-header">
        <div>
          <span className="section-label">AI ANALİZ ALANI</span>
          <h2>Şartnamenizi yükleyin</h2>
        </div>

        <span className="secure-label">Güvenli işlem</span>
      </div>

      <div
        className={`drop-zone ${isDragging ? "drop-zone--active" : ""}`}
        role="button"
        tabIndex={0}
        onClick={() => fileInputRef.current?.click()}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            fileInputRef.current?.click();
          }
        }}
        onDragEnter={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          className="file-input"
          type="file"
          accept=".pdf,.txt,.doc,.docx"
          onChange={handleFileChange}
        />

        <div className="upload-icon">
          <svg
            width="26"
            height="26"
            viewBox="0 0 24 24"
            fill="none"
            aria-hidden="true"
          >
            <path
              d="M12 16V4M12 4L7.5 8.5M12 4L16.5 8.5"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M5 14V18C5 19.1046 5.89543 20 7 20H17C18.1046 20 19 19.1046 19 18V14"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
            />
          </svg>
        </div>

        {file ? (
          <div className="selected-file">
            <div>
              <strong>{file.name}</strong>
              <span>{(file.size / 1024).toFixed(1)} KB</span>
            </div>

            <button type="button" onClick={removeFile}>
              Kaldır
            </button>
          </div>
        ) : (
          <>
            <strong>Dokümanı buraya sürükleyin</strong>
            <span>veya bilgisayarınızdan seçmek için tıklayın</span>
            <small>PDF, TXT, DOC ve DOCX desteklenir</small>
          </>
        )}
      </div>

      <div className="divider">
        <span />
        <small>VEYA METİN GİRİN</small>
        <span />
      </div>

      <label className="text-area-label" htmlFor="requirement-text">
        Şartname metni
      </label>

      <textarea
        id="requirement-text"
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder="Şartnamenin ilgili bölümünü buraya yapıştırabilirsiniz..."
        rows={6}
      />

      <div className="workspace-footer">
        <span>{text.length} karakter</span>

        <button
          className="analyze-button"
          type="button"
          disabled={isLoading}
          onClick={handleAnalyze}
        >
          {isLoading ? (
            <>
              <span className="spinner" />
              Şartname analiz ediliyor
            </>
          ) : (
            <>
              Analizi başlat
              <span aria-hidden="true">→</span>
            </>
          )}
        </button>
      </div>

      {error && <p className="form-error">{error}</p>}
    </section>
  );
}

export default UploadWorkspace;