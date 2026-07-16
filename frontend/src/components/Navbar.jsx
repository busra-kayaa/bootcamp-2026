function Navbar() {
  return (
    <header className="topbar">
      <a className="brand" href="#top" aria-label="SprintMate AI ana sayfa">
        <img
          className="brand-logo"
          src="/favicon.svg"
          alt="SprintMate AI logo"
        />

        <span className="brand-content">
          <strong>SprintMate AI</strong>
          <small>AI Project Planner</small>
        </span>
      </a>

      <nav className="nav-links" aria-label="Ana menü">
        <a href="#features">Özellikler</a>
        <a href="#workspace">Analiz</a>

        <span className="status-pill">
          <span className="status-dot" />
          MVP v0.2
        </span>
      </nav>
    </header>
  );
}

export default Navbar;