import React, { useRef, useState } from 'react'
import { uploadPDF } from '../services/api'
import './PDFUpload.css'

function PDFUpload({ onUploadStart, onUploadSuccess, onUploadError }) {
  const fileInputRef = useRef(null)
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState(null)

  const handleFile = async (file) => {
    if (!file) return

    if (!file.type.includes('pdf')) {
      setError('Please upload a PDF file')
      return
    }

    if (file.size > 50 * 1024 * 1024) {
      setError('File size must be less than 50MB')
      return
    }

    setError(null)
    onUploadStart()

    try {
      const response = await uploadPDF(file)
      onUploadSuccess(response.document_id, response.filename)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to upload file')
      if (onUploadError) {
        onUploadError()
      }
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const onButtonClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="upload-container">
      <div
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="upload-icon">📎</div>
        <h2 className="upload-title">Upload Research Paper</h2>
        <p className="upload-subtitle">
          Drag and drop your PDF file here, or click to browse
        </p>
        <button className="upload-button" onClick={onButtonClick}>
          Choose File
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleChange}
          style={{ display: 'none' }}
        />
        <p className="upload-hint">Maximum file size: 50MB</p>
        {error && <p className="upload-error">{error}</p>}
      </div>
    </div>
  )
}

export default PDFUpload

