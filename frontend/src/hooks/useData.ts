import { useState, useEffect } from 'react'
import { Note, Question } from '../types'
import { videoApi, examApi } from '../services/api'

interface Stats {
  totalNotes: number
  totalQuestions: number
  masteredQuestions: number
  masteryRate: number
}

export function useDashboardData(subject: 'adv_math' | 'ce') {
  const [notes, setNotes] = useState<Note[]>([])
  const [questions, setQuestions] = useState<Question[]>([])
  const [stats, setStats] = useState<Stats>({
    totalNotes: 0,
    totalQuestions: 0,
    masteredQuestions: 0,
    masteryRate: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)

      try {
        // 获取笔记列表
        const notesResponse = await videoApi.listNotes(subject)
        setNotes(notesResponse.notes || [])

        // 获取错题列表
        const questionsResponse = await examApi.listQuestions(subject)
        setQuestions(questionsResponse.questions || [])

        // 计算统计
        const totalQuestions = questionsResponse.questions?.length || 0
        const masteredQuestions = Math.floor(totalQuestions * 0.4) // TODO: 实际应从后端获取

        setStats({
          totalNotes: notesResponse.notes?.length || 0,
          totalQuestions,
          masteredQuestions,
          masteryRate: totalQuestions > 0 ? Math.round((masteredQuestions / totalQuestions) * 100) : 0
        })
      } catch (err) {
        setError(err instanceof Error ? err.message : '获取数据失败')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [subject])

  return { notes, questions, stats, loading, error }
}

export function useNotes(subject: 'adv_math' | 'ce') {
  const [notes, setNotes] = useState<Note[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchNotes = async () => {
      setLoading(true)
      try {
        const response = await videoApi.listNotes(subject)
        setNotes(response.notes || [])
      } catch {
        setNotes([])
      } finally {
        setLoading(false)
      }
    }

    fetchNotes()
  }, [subject])

  return { notes, loading }
}

export function useQuestions(subject: 'adv_math' | 'ce') {
  const [questions, setQuestions] = useState<Question[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchQuestions = async () => {
      setLoading(true)
      try {
        const response = await examApi.listQuestions(subject)
        setQuestions(response.questions || [])
      } catch {
        setQuestions([])
      } finally {
        setLoading(false)
      }
    }

    fetchQuestions()
  }, [subject])

  return { questions, loading }
}
