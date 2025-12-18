import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Upload a PDF file to the backend
 * @param {File} file - PDF file to upload
 * @returns {Promise} Response with document_id and processing info
 */
export const uploadPDF = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

/**
 * Send a chat message to the backend
 * @param {string} documentId - ID of the document
 * @param {string} question - User's question
 * @param {string} explanationLevel - Explanation level (beginner/student/researcher)
 * @param {Array} chatHistory - Previous chat messages
 * @returns {Promise} Response with answer and sources
 */
export const sendMessage = async (documentId, question, explanationLevel = 'student', chatHistory = []) => {
  const response = await api.post('/chat', {
    document_id: documentId,
    question,
    explanation_level: explanationLevel,
    chat_history: chatHistory,
  })

  return response.data
}

/**
 * Delete a document
 * @param {string} documentId - ID of the document to delete
 * @returns {Promise}
 */
export const deleteDocument = async (documentId) => {
  const response = await api.delete(`/documents/${documentId}`)
  return response.data
}

/**
 * Health check
 * @returns {Promise}
 */
export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

export default api

