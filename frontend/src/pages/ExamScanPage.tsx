import { useState, useRef } from 'react'

interface ExamScanPageProps {
  subject: 'adv_math' | 'ce'
}

export default function ExamScanPage({ subject }: ExamScanPageProps) {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      const reader = new FileReader()
      reader.onload = () => setPreview(reader.result as string)
      reader.readAsDataURL(selectedFile)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setIsProcessing(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('skill_type', subject)

      const response = await fetch('/api/exam/scan', {
        method: 'POST',
        body: formData
      })
      const data = await response.json()
      setResult(data)
    } catch {
      setResult({
        questions: [],
        summary: { totalErrors: 0, message: '试卷扫描功能即将上线' }
      })
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="exam-scan-page">
      <div className="page-header">
        <h1 className="page-title">📄 试卷扫描</h1>
        <p className="page-desc">
          上传试卷照片，AI将自动识别错题并分析原因
        </p>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*,.pdf"
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />

      {!preview ? (
        <div
          className="upload-area"
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="upload-area-icon">📷</div>
          <div className="upload-area-text">点击上传试卷图片</div>
          <div className="upload-area-hint">
            支持 JPG、PNG、PDF 格式
          </div>
        </div>
      ) : (
        <div style={{ marginBottom: '1rem', textAlign: 'center' }}>
          <img
            src={preview}
            alt="试卷预览"
            style={{
              maxWidth: '100%',
              maxHeight: '300px',
              borderRadius: '8px',
              border: '1px solid var(--border)'
            }}
          />
          <div style={{ marginTop: '0.5rem' }}>
            <button
              className="btn btn-secondary"
              onClick={() => {
                setPreview(null)
                setFile(null)
                setResult(null)
              }}
            >
              重新选择
            </button>
          </div>
        </div>
      )}

      {file && !result && (
        <button
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={isProcessing}
          style={{ width: '100%', padding: '0.75rem' }}
        >
          {isProcessing ? '识别中...' : '开始扫描'}
        </button>
      )}

      {isProcessing && (
        <div className="processing">
          <div className="processing-spinner">🔍</div>
          <div className="processing-text">正在识别试卷内容...</div>
        </div>
      )}

      {result && !isProcessing && (
        <div className="result-card">
          <div className="result-header">
            <span className="result-title">📊 扫描结果</span>
            <span className="result-badge">已完成</span>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <p>总错题数: <strong>{result.summary?.totalErrors || 0}</strong></p>
            {result.summary?.byType && (
              <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                {Object.entries(result.summary.byType).map(([type, count]) => (
                  <span key={type} style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    {type}: {count as number}
                  </span>
                ))}
              </div>
            )}
          </div>

          {result.message && (
            <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>
              {result.message}
            </p>
          )}

          {result.questions?.length > 0 && (
            <div style={{ marginTop: '1rem' }}>
              {result.questions.map((q: any, idx: number) => (
                <div
                  key={idx}
                  style={{
                    padding: '0.75rem',
                    background: 'var(--bg)',
                    borderRadius: '6px',
                    marginBottom: '0.5rem'
                  }}
                >
                  <p style={{ fontWeight: 600 }}>{q.text}</p>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                    错误类型: {q.error_type} | 知识点: {q.knowledge_points?.join(', ')}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
