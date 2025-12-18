import React, { useState, useRef, useEffect } from 'react'
import { sendMessage } from '../services/api'
import ExplanationLevelSelector from './ExplanationLevelSelector'
import './ChatInterface.css'

function ChatInterface({ documentId, documentName, onReset }) {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [explanationLevel, setExplanationLevel] = useState('student')
  const messagesEndRef = useRef(null)
  const chatContainerRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!inputValue.trim() || isLoading) return

    const question = inputValue.trim()
    const userMessage = {
      role: 'user',
      content: question
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      // Prepare chat history for context
      const chatHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      const response = await sendMessage(documentId, question, explanationLevel, chatHistory)
      
      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || error.message || 'Failed to get response'}`,
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-header-info">
          <h2 className="chat-title">Chat with Paper</h2>
          <p className="chat-document-name">{documentName}</p>
        </div>
        <div className="chat-header-actions">
          <ExplanationLevelSelector
            value={explanationLevel}
            onChange={setExplanationLevel}
          />
          <button className="reset-button" onClick={onReset}>
            New Paper
          </button>
        </div>
      </div>

      <div className="chat-messages" ref={chatContainerRef}>
        {messages.length === 0 && (
          <div className="welcome-message">
            <h3>Welcome! 👋</h3>
            <p>Ask me anything about the research paper. I can explain:</p>
            <ul>
              <li>Key concepts and methodologies</li>
              <li>Equations and formulas</li>
              <li>Results and conclusions</li>
              <li>Implementation details</li>
            </ul>
            <p className="welcome-hint">
              Select your preferred explanation level above: Beginner, Student, or Researcher
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-content">
              {message.role === 'user' ? (
                <div className="message-bubble user-bubble">
                  {message.content}
                </div>
              ) : (
                <div className={`message-bubble assistant-bubble ${message.isError ? 'error' : ''}`}>
                  {message.content}
                  {message.sources && message.sources.length > 0 && (
                    <div className="sources">
                      <strong>Relevant sources:</strong>
                      {message.sources.map((source, idx) => (
                        <div key={idx} className="source-item">
                          {source}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="message-bubble assistant-bubble loading">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSend}>
        <input
          type="text"
          className="chat-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask a question about the research paper..."
          disabled={isLoading}
        />
        <button
          type="submit"
          className="send-button"
          disabled={isLoading || !inputValue.trim()}
        >
          Send
        </button>
      </form>
    </div>
  )
}

export default ChatInterface

