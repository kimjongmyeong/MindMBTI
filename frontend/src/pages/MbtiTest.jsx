import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getQuestions, submitAnswers } from '../api'

export default function MbtiTest() {
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [current, setCurrent] = useState(0)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    getQuestions().then(setQuestions).catch(console.error).finally(() => setLoading(false))
  }, [])

  const handleAnswer = (qid, value) => {
    setAnswers((prev) => ({ ...prev, [qid]: value }))
  }

  const handleNext = () => {
    if (current < questions.length - 1) setCurrent((c) => c + 1)
    else handleSubmit()
  }

  const handlePrev = () => {
    if (current > 0) setCurrent((c) => c - 1)
  }

  const handleSubmit = async () => {
    if (Object.keys(answers).length < 48) return
    setSubmitting(true)
    try {
      const arr = Object.entries(answers).map(([q, v]) => ({ question_id: +q, value: +v }))
      const { session_id } = await submitAnswers(arr)
      navigate(`/result/${session_id}`)
    } catch (err) {
      alert(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div className="page"><p>로딩 중...</p></div>
  if (!questions.length) return <div className="page"><p>문항을 불러올 수 없습니다.</p></div>

  const q = questions[current]
  const progress = ((current + 1) / questions.length) * 100

  return (
    <div className="page mbti-test">
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>
      <p className="progress-text">{current + 1} / {questions.length}</p>
      <div className="question-card">
        <p className="dimension">{q.dimension}</p>
        <h2>{q.text}</h2>
        <div className="likert">
          {[1, 2, 3, 4, 5].map((v) => (
            <label key={v} className={answers[q.id] === v ? 'selected' : ''}>
              <input
                type="radio"
                name={`q${q.id}`}
                value={v}
                checked={answers[q.id] === v}
                onChange={() => handleAnswer(q.id, v)}
              />
              <span>{v}</span>
            </label>
          ))}
        </div>
        <p className="likert-label">전혀 아님(1) ←→ 매우 그렇다(5)</p>
      </div>
      <div className="nav-btns">
        <button onClick={handlePrev} disabled={current === 0}>이전</button>
        <button onClick={handleNext} disabled={!answers[q.id] || submitting}>
          {current === questions.length - 1 ? '결과 보기' : '다음'}
        </button>
      </div>
    </div>
  )
}
