import { useState, useRef } from 'react'

interface FileUploaderProps {
  onUploaded: () => void
  message: string
  onMessageChange: (msg: string) => void
}

export default function FileUploader({ onUploaded, message, onMessageChange }: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      uploadFile(files[0])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      uploadFile(files[0])
    }
  }

  const uploadFile = async (file: File) => {
    const allowedTypes = ['application/pdf', 'text/plain', 'text/markdown']
    const allowedExtensions = ['.pdf', '.txt', '.md']
    
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      onMessageChange('Unsupported file type. Only PDF, TXT, and MD files are allowed.')
      setTimeout(() => onMessageChange(''), 3000)
      return
    }

    setIsUploading(true)
    onMessageChange('')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/rag/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const result = await response.json()
      onMessageChange(`✓ ${result.fileName} uploaded successfully`)
      setTimeout(() => onMessageChange(''), 3000)
      onUploaded()
    } catch (error) {
      onMessageChange('✗ Upload failed. Please try again.')
      setTimeout(() => onMessageChange(''), 3000)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
      <h2 className="text-lg font-semibold text-white mb-4">Upload Documents</h2>
      
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-all cursor-pointer ${
          isDragging 
            ? 'border-purple-500 bg-purple-500/20' 
            : 'border-white/30 hover:border-white/50 hover:bg-white/5'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.md"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <div className="flex flex-col items-center gap-3">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
            isUploading ? 'bg-purple-500/30' : 'bg-purple-500/20'
          }`}>
            {isUploading ? (
              <svg className="w-8 h-8 text-purple-400 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            ) : (
              <svg className="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            )}
          </div>
          
          <div>
            <p className="text-white font-medium">
              {isUploading ? 'Uploading...' : 'Drag files here or click to browse'}
            </p>
            <p className="text-white/50 text-sm mt-1">
              Supports PDF, TXT, MD files
            </p>
          </div>
        </div>
      </div>

      {message && (
        <div className={`mt-4 p-3 rounded-lg text-sm ${
          message.includes('successfully') 
            ? 'bg-green-500/20 text-green-400' 
            : message.includes('failed')
            ? 'bg-red-500/20 text-red-400'
            : 'bg-yellow-500/20 text-yellow-400'
        }`}>
          {message}
        </div>
      )}

      <div className="mt-6 p-4 bg-white/5 rounded-lg">
        <h3 className="text-white/80 text-sm font-medium mb-2">How to use:</h3>
        <ol className="text-white/60 text-sm space-y-1">
          <li>1. Upload your documents (PDF, TXT, MD)</li>
          <li>2. Wait for processing</li>
          <li>3. Ask questions about your documents</li>
        </ol>
      </div>
    </div>
  )
}
