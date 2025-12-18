import React from 'react'
import './Header.css'

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <h1 className="header-title">
          <span className="header-icon">📄</span>
          PaperLens
        </h1>
        <p className="header-subtitle">AI-Powered Research Paper Explainer</p>
      </div>
    </header>
  )
}

export default Header

