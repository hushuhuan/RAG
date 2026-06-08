import { useState } from 'react'
import FileUploader from './components/FileUploader'
import ChatPanel from './components/ChatPanel'
import StatsPanel from './components/StatsPanel'
import './App.css'

function App() {
  const [documentsCount, setDocumentsCount] = useState(0)
  const [uploadMessage, setUploadMessage] = useState('')

  const handleFileUploaded = () => {
    fetch('/api/rag/stats')
      .then(res => res.json())
      .then(data => setDocumentsCount(data.count))
      .catch(err => console.error('Failed to fetch stats:', err))
  }

  const handleClearDocuments = () => {
    fetch('/api/rag/clear', { method: 'DELETE' })
      .then(res => res.json())
      .then(() => {
        setDocumentsCount(0)
        setUploadMessage('All documents cleared')
        setTimeout(() => setUploadMessage(''), 3000)
      })
      .catch(err => console.error('Failed to clear:', err))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <header className="bg-black/30 backdrop-blur-md border-b border-white/10">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h1 className="text-xl font-bold text-white">RAG LangGraph</h1>
            </div>
            <StatsPanel count={documentsCount} onClear={handleClearDocuments} />
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <FileUploader 
              onUploaded={handleFileUploaded} 
              message={uploadMessage}
              onMessageChange={setUploadMessage}
            />
          </div>
          <div className="lg:col-span-2">
            <ChatPanel />
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
