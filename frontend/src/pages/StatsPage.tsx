import { useState } from 'react'
import { Question } from '../types'

interface StatsPageProps {
  subject?: 'adv_math' | 'ce'
}

const mockQuestions: Question[] = [
  {
    id: '1',
    text: '设 f(x) = x²，求 lim(x→0) f(x)/x',
    answer: '0',
    errorType: 'calculation',
    knowledgePoints: ['极限', '洛必达法则'],
    difficulty: 2
  },
  {
    id: '2',
    text: '证明 lim(x→0) sin(x)/x = 1',
    answer: '利用夹逼准则',
    errorType: 'concept',
    knowledgePoints: ['极限', '夹逼准则', '三角函数'],
    difficulty: 3
  },
  {
    id: '3',
    text: '设函数 f(x) 在 x=0 处连续，则 f(0) = ?',
    answer: '需要更多条件',
    errorType: 'logic',
    knowledgePoints: ['连续', '极限'],
    difficulty: 2
  }
]

export default function StatsPage(_props: StatsPageProps) {
  const [filter, setFilter] = useState<string>('all')
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null)

  // 后续根据subject过滤对应科目的错题
  const subjectQuestions = mockQuestions // TODO: filter by subject

  const errorTypes = ['all', 'calculation', 'concept', 'logic', 'reading']
  const errorTypeLabels: Record<string, string> = {
    all: '全部',
    calculation: '计算失误',
    concept: '概念混淆',
    logic: '思路错误',
    reading: '审题不清'
  }

  const filteredQuestions = filter === 'all'
    ? subjectQuestions
    : subjectQuestions.filter(q => q.errorType === filter)

  return (
    <div className="stats-page">
      <div className="page-header">
        <h1 className="page-title">📚 错题本</h1>
        <p className="page-desc">
          系统化管理错题，分析错误原因，关联知识点
        </p>
      </div>

      {/* 统计卡片 */}
      <div className="func-cards" style={{ marginBottom: '1.5rem' }}>
        <div className="func-card">
          <div className="func-card-icon">📊</div>
          <div className="func-card-title">总错题数</div>
          <div className="func-card-desc">{mockQuestions.length} 题</div>
        </div>
        <div className="func-card">
          <div className="func-card-icon">🎯</div>
          <div className="func-card-title">已掌握</div>
          <div className="func-card-desc">12 题</div>
        </div>
        <div className="func-card">
          <div className="func-card-icon">📈</div>
          <div className="func-card-title">掌握率</div>
          <div className="func-card-desc">78%</div>
        </div>
      </div>

      {/* 筛选 */}
      <div style={{ marginBottom: '1rem' }}>
        <h3 className="section-title">筛选错题</h3>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {errorTypes.map(type => (
            <button
              key={type}
              className={`btn ${filter === type ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilter(type)}
            >
              {errorTypeLabels[type]}
            </button>
          ))}
        </div>
      </div>

      {/* 错题列表 */}
      <div className="notes-list">
        {filteredQuestions.map(q => (
          <div
            key={q.id}
            className="note-item"
            onClick={() => setSelectedQuestion(q)}
            style={{ cursor: 'pointer' }}
          >
            <div className="note-item-header">
              <span className="note-item-title">
                {q.errorType && (
                  <span style={{
                    marginRight: '0.5rem',
                    padding: '0.1rem 0.4rem',
                    background: 'var(--danger)',
                    color: 'white',
                    borderRadius: '4px',
                    fontSize: '0.75rem'
                  }}>
                    {errorTypeLabels[q.errorType]}
                  </span>
                )}
                难度: {q.difficulty}/5
              </span>
            </div>
            <p className="note-item-preview" style={{ marginBottom: '0.5rem' }}>
              {q.text}
            </p>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              知识点: {q.knowledgePoints.join(' · ')}
            </div>
            <div className="note-item-actions">
              <button className="btn btn-primary">复习</button>
              <button className="btn btn-secondary">查看解析</button>
            </div>
          </div>
        ))}
      </div>

      {/* 错题详情弹窗 */}
      {selectedQuestion && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
          onClick={() => setSelectedQuestion(null)}
        >
          <div
            style={{
              background: 'white',
              padding: '1.5rem',
              borderRadius: '12px',
              maxWidth: '500px',
              width: '90%'
            }}
            onClick={e => e.stopPropagation()}
          >
            <h3 style={{ marginBottom: '1rem' }}>错题详情</h3>
            <div style={{ marginBottom: '1rem' }}>
              <p style={{ fontWeight: 600 }}>题目:</p>
              <p>{selectedQuestion.text}</p>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <p style={{ fontWeight: 600 }}>正确答案:</p>
              <p>{selectedQuestion.answer}</p>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <p style={{ fontWeight: 600 }}>错误类型:</p>
              <p>{errorTypeLabels[selectedQuestion.errorType || 'all']}</p>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <p style={{ fontWeight: 600 }}>相关知识点:</p>
              <p>{selectedQuestion.knowledgePoints.join(' · ')}</p>
            </div>
            <button
              className="btn btn-primary"
              style={{ width: '100%' }}
              onClick={() => setSelectedQuestion(null)}
            >
              关闭
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
