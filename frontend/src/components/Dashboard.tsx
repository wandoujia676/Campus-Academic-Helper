import { Note, ErrorWarning } from '../types'
import { useDashboardData } from '../hooks/useData'

interface DashboardProps {
  onNavigate: (page: 'dashboard' | 'video' | 'exam' | 'stats') => void
  subject: 'adv_math' | 'ce'
  onSubjectChange: (subject: 'adv_math' | 'ce') => void
}

const ERROR_WARNING_MOCK: ErrorWarning = {
  topic: '极限计算',
  errorCount: 5,
  masteryLevel: 30
}

export default function Dashboard({ onNavigate, subject }: DashboardProps) {
  const { notes, stats, loading } = useDashboardData(subject)
  const subjectName = subject === 'adv_math' ? '高等数学' : '大学英语'

  return (
    <div className="dashboard">
      {/* 功能卡片 */}
      <section className="func-cards">
        <div className="func-card" onClick={() => onNavigate('video')}>
          <div className="func-card-icon">📹</div>
          <div className="func-card-title">视频笔记</div>
          <div className="func-card-desc">
            {loading ? '加载中...' : `已生成 ${stats.totalNotes} 篇`}
          </div>
        </div>
        <div className="func-card" onClick={() => onNavigate('exam')}>
          <div className="func-card-icon">📄</div>
          <div className="func-card-title">试卷扫描</div>
          <div className="func-card-desc">上传试卷识别错题</div>
        </div>
        <div className="func-card" onClick={() => onNavigate('stats')}>
          <div className="func-card-icon">📚</div>
          <div className="func-card-title">错题本</div>
          <div className="func-card-desc">
            {loading ? '加载中...' : `共 ${stats.totalQuestions} 题`}
          </div>
        </div>
        <div className="func-card" onClick={() => onNavigate('stats')}>
          <div className="func-card-icon">✍️</div>
          <div className="func-card-title">练习中心</div>
          <div className="func-card-desc">
            {loading ? '加载中...' : `完成 ${stats.masteredQuestions} 题`}
          </div>
        </div>
      </section>

      {/* 最近笔记 */}
      <section>
        <h2 className="section-title">最近笔记 - {subjectName}</h2>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            加载中...
          </div>
        ) : notes.length > 0 ? (
          <div className="notes-list">
            {notes.slice(0, 3).map((note: Note) => (
              <div key={note.id} className="note-item">
                <div className="note-item-header">
                  <span className="note-item-title">📑 {note.title}</span>
                  <span className="note-item-date">{note.date}</span>
                </div>
                <p className="note-item-preview">{note.preview}</p>
                <div className="note-item-actions">
                  <button className="btn btn-primary">查看笔记</button>
                  <button className="btn btn-secondary">生成练习</button>
                  <button className="btn btn-secondary">编辑</button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            暂无笔记，请先上传视频生成笔记
          </div>
        )}
      </section>

      {/* 错题预警 */}
      <section>
        <h2 className="section-title">错题预警 - {subjectName}</h2>
        <div className="error-warning">
          <div className="error-warning-header">
            <span className="error-warning-title">⚠️ {ERROR_WARNING_MOCK.topic}</span>
            <div className="error-warning-stats">
              <span>出错: {ERROR_WARNING_MOCK.errorCount}次</span>
              <span>掌握度: {ERROR_WARNING_MOCK.masteryLevel}%</span>
            </div>
          </div>
          <div className="progress-bar">
            <div
              className="progress-bar-fill"
              style={{ width: `${ERROR_WARNING_MOCK.masteryLevel}%` }}
            />
          </div>
          <div style={{ marginTop: '0.75rem', textAlign: 'right' }}>
            <button className="btn btn-primary">立即复习</button>
          </div>
        </div>
      </section>

      {/* 学习统计 */}
      <section>
        <h2 className="section-title">学习统计 - {subjectName}</h2>
        <div className="func-cards" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
          <div className="func-card">
            <div className="func-card-icon">📊</div>
            <div className="func-card-title">总错题</div>
            <div className="func-card-desc">{stats.totalQuestions} 题</div>
          </div>
          <div className="func-card">
            <div className="func-card-icon">🎯</div>
            <div className="func-card-title">已掌握</div>
            <div className="func-card-desc">{stats.masteredQuestions} 题</div>
          </div>
          <div className="func-card">
            <div className="func-card-icon">📈</div>
            <div className="func-card-title">掌握率</div>
            <div className="func-card-desc">{stats.masteryRate}%</div>
          </div>
        </div>
      </section>
    </div>
  )
}
