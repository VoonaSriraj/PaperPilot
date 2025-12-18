import React, { useState } from 'react'
import './App.css'
import PDFUpload from './components/PDFUpload'
import ChatInterface from './components/ChatInterface'
import Header from './components/Header'

function App() {
  const [documentId, setDocumentId] = useState(null)
  const [documentName, setDocumentName] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleUploadSuccess = (docId, filename) => {
    setDocumentId(docId)
    setDocumentName(filename)
    setIsProcessing(false)
  }

  const handleUploadStart = () => {
    setIsProcessing(true)
    setDocumentId(null)
    setDocumentName(null)
  }

  const handleUploadError = () => {
    setIsProcessing(false)
    setDocumentId(null)
    setDocumentName(null)
  }

  const handleReset = () => {
    setDocumentId(null)
    setDocumentName(null)
    setIsProcessing(false)
  }

  return (
    <div className="app">
      <Header />
      <main className="main-content">
        {!documentId && !isProcessing ? (
          <PDFUpload
            onUploadStart={handleUploadStart}
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        ) : isProcessing ? (
          <div className="processing-container">
            <div className="spinner"></div>
            <p>Processing your research paper...</p>
            <p className="processing-subtitle">This may take a few moments</p>
          </div>
        ) : (
          <ChatInterface
            documentId={documentId}
            documentName={documentName}
            onReset={handleReset}
          />
        )}
      </main>
    </div>
  )
}

export default App

