import React from 'react'
import './ExplanationLevelSelector.css'

function ExplanationLevelSelector({ value, onChange }) {
  const levels = [
    { id: 'beginner', label: 'Beginner', icon: '🌱' },
    { id: 'student', label: 'Student', icon: '🎓' },
    { id: 'researcher', label: 'Researcher', icon: '🔬' }
  ]

  return (
    <div className="level-selector">
      <label className="level-selector-label">Level:</label>
      <div className="level-buttons">
        {levels.map(level => (
          <button
            key={level.id}
            className={`level-button ${value === level.id ? 'active' : ''}`}
            onClick={() => onChange(level.id)}
            title={`${level.label} level explanation`}
          >
            <span className="level-icon">{level.icon}</span>
            <span className="level-label">{level.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

export default ExplanationLevelSelector

