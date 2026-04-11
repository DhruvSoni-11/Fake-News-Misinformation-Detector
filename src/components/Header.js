import React from 'react';
import './Header.css';

function Header() {
  return (
    <header className="header">
      <div className="header-inner">
        <div className="logo">
          <span className="logo-icon">⬡</span>
          <span className="logo-text">TRUTH<span className="logo-accent">SCAN</span></span>
        </div>
        <nav className="nav">
          <span className="nav-badge">NLP · Credibility · Sources</span>
        </nav>
      </div>
      <div className="header-scanline" />
    </header>
  );
}

export default Header;