import { useState } from 'react'
import Dashboard from './components/Dashboard'
import VideoNotesPage from './pages/VideoNotesPage'
import ExamScanPage from './pages/ExamScanPage'
import StatsPage from './pages/StatsPage'

type Page = 'dashboard' | 'video' | 'exam' | 'stats'

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard')
  const [currentSubject, setCurrentSubject] = useState<'adv_math' | 'ce'>('adv_math')

  const renderPage = () => {
    switch (currentPage) {
      case 'video':
        return <VideoNotesPage subject={currentSubject} />
      case 'exam':
        return <ExamScanPage subject={currentSubject} />
      case 'stats':
        return <StatsPage subject={currentSubject} />
      default:
        return <Dashboard onNavigate={setCurrentPage} subject={currentSubject} onSubjectChange={setCurrentSubject} />
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <h1>🎓 乐乐学业助手</h1>
        </div>
        <div className="header-center">
          <select
            value={currentSubject}
            onChange={(e) => setCurrentSubject(e.target.value as 'adv_math' | 'ce')}
            className="subject-select"
          >
            <option value="adv_math">📐 高等数学</option>
            <option value="ce">📝 大学英语</option>
          </select>
        </div>
        <div className="header-right">
          <span className="user-badge">👤 乐乐</span>
          <button className="settings-btn">⚙️ 设置</button>
        </div>
      </header>

      <main className="app-main">
        {renderPage()}
      </main>

      <nav className="bottom-nav">
        <button onClick={() => setCurrentPage('dashboard')} className={currentPage === 'dashboard' ? 'active' : ''}>
          📊 首页
        </button>
        <button onClick={() => setCurrentPage('video')} className={currentPage === 'video' ? 'active' : ''}>
          📹 视频笔记
        </button>
        <button onClick={() => setCurrentPage('exam')} className={currentPage === 'exam' ? 'active' : ''}>
          📄 试卷扫描
        </button>
        <button onClick={() => setCurrentPage('stats')} className={currentPage === 'stats' ? 'active' : ''}>
          📚 错题本
        </button>
      </nav>
    </div>
  )
}

export default App
