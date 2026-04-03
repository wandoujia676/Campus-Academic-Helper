import { Note, ErrorWarning } from '../types'

interface DashboardProps {
  onNavigate: (page: 'dashboard' | 'video' | 'exam' | 'stats') => void
  subject: 'adv_math' | 'ce'
  onSubjectChange: (subject: 'adv_math' | 'ce') => void
}

const mockNotes: Note[] = [
  {
    id: '1',
    title: '第3章 导数与微分',
    date: '2024-03-15',
    preview: '理解导数的几何意义，掌握基本求导法则...',
    skillType: 'adv_math'
  },
  {
    id: '2',
    title: '第2章 极限与连续',
    date: '2024-03-10',
    preview: '掌握数列极限和函数极限的概念...',
    skillType: 'adv_math'
  }
]

const mockErrorWarning: ErrorWarning = {
  topic: '极限计算',
  errorCount: 5,
  masteryLevel: 30
}

export default function Dashboard({ onNavigate, subject }: DashboardProps) {
  const subjectName = subject === 'adv_math' ? '高等数学' : '大学英语'

  return (
    <div className="dashboard">
      {/* 功能卡片 */}
      <section className="func-cards">
        <div className="func-card" onClick={() => onNavigate('video')}>
          <div className="func-card-icon">📹</div>
          <div className="func-card-title">视频笔记</div>
          <div className="func-card-desc">今日: 0</div>
        </div>
        <div className="func-card" onClick={() => onNavigate('exam')}>
          <div className="func-card-icon">📄</div>
          <div className="func-card-title">试卷扫描</div>
          <div className="func-card-desc">待处理: 2</div>
        </div>
        <div className="func-card" onClick={() => onNavigate('stats')}>
          <div className="func-card-icon">📚</div>
          <div className="func-card-title">错题本</div>
          <div className="func-card-desc">共: 28题</div>
        </div>
        <div className="func-card" onClick={() => onNavigate('stats')}>
          <div className="func-card-icon">✍️</div>
          <div className="func-card-title">练习中心</div>
          <div className="func-card-desc">完成: 15题</div>
        </div>
      </section>

      {/* 最近笔记 */}
      <section>
        <h2 className="section-title">最近笔记 - {subjectName}</h2>
        <div className="notes-list">
          {mockNotes.filter(n => n.skillType === subject).map(note => (
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
      </section>

      {/* 错题预警 */}
      <section>
        <h2 className="section-title">错题预警 - {subjectName}</h2>
        <div className="error-warning">
          <div className="error-warning-header">
            <span className="error-warning-title">⚠️ {mockErrorWarning.topic}</span>
            <div className="error-warning-stats">
              <span>出错: {mockErrorWarning.errorCount}次</span>
              <span>掌握度: {mockErrorWarning.masteryLevel}%</span>
            </div>
          </div>
          <div className="progress-bar">
            <div
              className="progress-bar-fill"
              style={{ width: `${mockErrorWarning.masteryLevel}%` }}
            />
          </div>
          <div style={{ marginTop: '0.75rem', textAlign: 'right' }}>
            <button className="btn btn-primary">立即复习</button>
          </div>
        </div>
      </section>
    </div>
  )
}
