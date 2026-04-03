export interface Note {
  id: string
  title: string
  date: string
  preview: string
  skillType: 'adv_math' | 'ce'
}

export interface ErrorWarning {
  topic: string
  errorCount: number
  masteryLevel: number
}

export interface Question {
  id: string
  text: string
  answer: string
  errorType?: 'calculation' | 'concept' | 'logic' | 'reading'
  knowledgePoints: string[]
  difficulty: number
}

export interface VideoNote {
  id: string
  url: string
  title: string
  chapters: Chapter[]
  markdown: string
  exercises: Exercise[]
}

export interface Chapter {
  id: string
  title: string
  startTime: number
  endTime: number
  content: string
}

export interface Exercise {
  id: string
  type: 'choice' | 'fill' | 'calc' | 'proof'
  question: string
  answer: string
  explanation?: string
  difficulty: number
}

export interface ExamScanResult {
  id: string
  questions: Question[]
  summary: {
    totalErrors: number
    byType: Record<string, number>
  }
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}
