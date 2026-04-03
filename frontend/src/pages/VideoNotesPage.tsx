import { useState } from 'react'
import { VideoNote, ApiResponse } from '../types'

interface VideoNotesPageProps {
  subject: 'adv_math' | 'ce'
}

type ProcessingStep = 'idle' | 'downloading' | 'transcribing' | 'analyzing' | 'completed' | 'error'

const stepLabels: Record<ProcessingStep, string> = {
  idle: '',
  downloading: '下载视频中...',
  transcribing: '语音识别中...',
  analyzing: 'AI分析中...',
  completed: '完成',
  error: '出错'
}

export default function VideoNotesPage({ subject }: VideoNotesPageProps) {
  const [url, setUrl] = useState('')
  const [step, setStep] = useState<ProcessingStep>('idle')
  const [note, setNote] = useState<VideoNote | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return

    setStep('downloading')
    setError(null)
    setNote(null)

    try {
      // Step 1: 下载视频
      setStep('downloading')
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Step 2: 语音识别
      setStep('transcribing')
      await new Promise(resolve => setTimeout(resolve, 1500))

      // Step 3: AI分析
      setStep('analyzing')
      const response = await fetch('/api/video/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, skill_type: subject })
      })

      const data: ApiResponse<VideoNote> = await response.json()

      if (!response.ok) {
        throw new Error(data.error || '生成失败')
      }

      setNote(data.data || null)
      setStep('completed')
    } catch (err) {
      setError(err instanceof Error ? err.message : '视频笔记功能暂时不可用')
      setStep('error')
    }
  }

  const reset = () => {
    setStep('idle')
    setNote(null)
    setError(null)
    setUrl('')
  }

  return (
    <div className="video-notes-page">
      <div className="page-header">
        <h1 className="page-title">📹 视频笔记生成</h1>
        <p className="page-desc">
          粘贴课程视频链接，AI将自动分析内容并生成结构化章节笔记
        </p>
      </div>

      {step === 'idle' && (
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
            disabled={!url.trim()}
            style={{ width: '100%', padding: '0.75rem' }}
          >
            生成笔记
          </button>
        </form>
      )}

      {step !== 'idle' && step !== 'completed' && step !== 'error' && (
        <div className="processing">
          <div className="processing-spinner">⏳</div>
          <div className="processing-text">{stepLabels[step]}</div>
          <div style={{ marginTop: '1rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            {step === 'downloading' && '正在连接视频服务器...'}
            {step === 'transcribing' && '正在将语音转换为文字...'}
            {step === 'analyzing' && '正在分析课程内容，生成笔记...'}
          </div>
        </div>
      )}

      {step === 'error' && (
        <div className="result-card" style={{ borderLeftColor: 'var(--danger)' }}>
          <div className="result-header">
            <span className="result-title" style={{ color: 'var(--danger)' }}>❌ 生成失败</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>{error}</p>
          <button className="btn btn-primary" onClick={reset}>
            重新尝试
          </button>
        </div>
      )}

      {step === 'completed' && note && (
        <div className="result-card">
          <div className="result-header">
            <span className="result-title">📝 {note.metadata?.title || '生成的笔记'}</span>
            <span className="result-badge">已完成</span>
          </div>

          {/* 章节信息 */}
          {note.metadata?.chapters && note.metadata.chapters.length > 0 && (
            <div style={{ marginBottom: '1rem' }}>
              <h4 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                📚 章节列表
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {note.metadata.chapters.map((ch, idx) => (
                  <span
                    key={idx}
                    style={{
                      padding: '0.25rem 0.75rem',
                      background: 'var(--bg)',
                      borderRadius: '12px',
                      fontSize: '0.8rem'
                    }}
                  >
                    {ch.title}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* 笔记内容 */}
          <pre style={{
            whiteSpace: 'pre-wrap',
            fontSize: '0.85rem',
            maxHeight: '400px',
            overflow: 'auto',
            padding: '1rem',
            background: 'var(--bg)',
            borderRadius: '8px'
          }}>
            {note.markdown || '笔记内容'}
          </pre>

          {/* 练习题 */}
          {note.exercises && note.exercises.length > 0 && (
            <div style={{ marginTop: '1rem' }}>
              <h4 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                ✍️ 配套练习
              </h4>
              {note.exercises.map((ex, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '0.75rem',
                    background: 'var(--bg)',
                    borderRadius: '6px',
                    marginBottom: '0.5rem'
                  }}
                >
                  <p style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                    {idx + 1}. {ex.question}
                  </p>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    答案: {ex.answer}
                  </p>
                </div>
              ))}
            </div>
          )}

          <div style={{ marginTop: '1rem', textAlign: 'right' }}>
            <button className="btn btn-secondary" onClick={reset}>
              生成新笔记
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
