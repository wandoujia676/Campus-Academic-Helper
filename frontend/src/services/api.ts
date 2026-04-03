/**
 * API Service
 * 统一处理与后端的API通信
 */
import { VideoNote, ExamScanResult, Note, Question, ApiResponse } from '../types'

const API_BASE = '/api'

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }
  return response.json()
}

// 视频笔记API
export const videoApi = {
  /**
   * 生成视频笔记
   */
  async generateNotes(url: string, skillType: 'adv_math' | 'ce'): Promise<ApiResponse<VideoNote>> {
    const response = await fetch(`${API_BASE}/video/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, skill_type: skillType })
    })
    return handleResponse<ApiResponse<VideoNote>>(response)
  },

  /**
   * 获取笔记列表
   */
  async listNotes(skillType?: string): Promise<{ notes: Note[] }> {
    const params = skillType ? `?skill_type=${skillType}` : ''
    const response = await fetch(`${API_BASE}/video/notes${params}`)
    return handleResponse<{ notes: Note[] }>(response)
  },

  /**
   * 获取单个笔记
   */
  async getNote(noteId: string): Promise<Note> {
    const response = await fetch(`${API_BASE}/video/notes/${noteId}`)
    return handleResponse<Note>(response)
  }
}

// 试卷扫描API
export const examApi = {
  /**
   * 扫描试卷
   */
  async scanExam(file: File, skillType: 'adv_math' | 'ce'): Promise<ExamScanResult> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('skill_type', skillType)

    const response = await fetch(`${API_BASE}/exam/scan`, {
      method: 'POST',
      body: formData
    })
    return handleResponse<ExamScanResult>(response)
  },

  /**
   * 获取错题列表
   */
  async listQuestions(skillType?: string, errorType?: string): Promise<{ questions: Question[] }> {
    const params = new URLSearchParams()
    if (skillType) params.append('skill_type', skillType)
    if (errorType) params.append('error_type', errorType)
    const queryString = params.toString()
    const response = await fetch(`${API_BASE}/exam/questions${queryString ? `?${queryString}` : ''}`)
    return handleResponse<{ questions: Question[] }>(response)
  },

  /**
   * 获取单个错题
   */
  async getQuestion(questionId: string): Promise<Question> {
    const response = await fetch(`${API_BASE}/exam/questions/${questionId}`)
    return handleResponse<Question>(response)
  }
}

// 同步API
export const syncApi = {
  async pushToCloud(): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE}/sync/push`, { method: 'POST' })
    return handleResponse(response)
  },

  async pullFromCloud(tableName: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE}/sync/pull?table_name=${tableName}`, { method: 'POST' })
    return handleResponse(response)
  },

  async getStatus(): Promise<{ synced: boolean; pending_tables: { table_name: string; pending: number }[] }> {
    const response = await fetch(`${API_BASE}/sync/status`)
    return handleResponse(response)
  }
}
