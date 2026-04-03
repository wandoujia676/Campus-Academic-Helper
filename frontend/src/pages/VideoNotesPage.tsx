import { useState } from 'react'

interface VideoNotesPageProps {
  subject: 'adv_math' | 'ce'
}

export default function VideoNotesPage({ subject }: VideoNotesPageProps) {
  const [url, setUrl] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return

    setIsProcessing(true)
    try {
      const response = await fetch('/api/video/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, skill_type: subject })
      })
      const data = await response.json()
      setResult(data.markdown || '笔记生成完成！')
    } catch {
      setResult('视频笔记功能即将上线，请稍候...')
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="video-notes-page">
      <div className="page-header">
        <h1 className="page-title">📹 视频笔记生成</h1>
        <p className="page-desc">
          粘贴课程视频链接，AI将自动分析内容并生成结构化章节笔记
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="upload-area" style={{ marginBottom: '1rem' }}>
          <div className="upload-area-icon">🎬</div>
          <div className="upload-area-text">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="粘贴视频链接，如：https://www.bilibili.com/video/BV1xx4y1m7"
              style={{
                width: '100%',
                maxWidth: '500px',
                padding: '0.75rem',
                border: '1px solid var(--border)',
                borderRadius: '6px',
                fontSize: '0.9rem'
              }}
            />
          </div>
          <div className="upload-area-hint">
            支持 B站、YouTube、学校平台等主流视频链接
          </div>
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          disabled={isProcessing || !url.trim()}
          style={{ width: '100%', padding: '0.75rem' }}
        >
          {isProcessing ? '分析中...' : '生成笔记'}
        </button>
      </form>

      {isProcessing && (
        <div className="processing">
          <div className="processing-spinner">⏳</div>
          <div className="processing-text">正在解析视频，请稍候...</div>
        </div>
      )}

      {result && !isProcessing && (
        <div className="result-card">
          <div className="result-header">
            <span className="result-title">📝 生成的笔记</span>
            <span className="result-badge">已完成</span>
          </div>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem' }}>
            {result}
          </pre>
        </div>
      )}
    </div>
  )
}
