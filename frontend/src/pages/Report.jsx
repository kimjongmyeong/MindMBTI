import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getBasicReport, getAiReport } from '../api'

const TYPES = ['INTJ','INTP','ENTJ','ENTP','INFJ','INFP','ENFJ','ENFP','ISTJ','ISFJ','ESTJ','ESFJ','ISTP','ISFP','ESTP','ESFP']

export default function Report() {
  const [searchParams] = useSearchParams()
  const initType = searchParams.get('type') || 'ENFP'
  const [mbtiType, setMbtiType] = useState(initType)
  const [basic, setBasic] = useState(null)
  const [ai, setAi] = useState(null)
  const [job, setJob] = useState('')
  const [concern, setConcern] = useState('')
  const [relConcern, setRelConcern] = useState('')
  const [loadingAi, setLoadingAi] = useState(false)

  useEffect(() => {
    getBasicReport(mbtiType).then(setBasic).catch(console.error)
    setAi(null)
  }, [mbtiType])

  const handleAiReport = async () => {
    setLoadingAi(true)
    try {
      const d = await getAiReport(mbtiType, job || undefined, concern || undefined, relConcern || undefined)
      setAi(d.ai_interpretation)
    } catch (e) {
      alert(e.message)
    } finally {
      setLoadingAi(false)
    }
  }

  return (
    <div className="page report-page">
      <h1>리포트</h1>
      <div className="type-select">
        <label>MBTI 유형</label>
        <select value={mbtiType} onChange={(e) => setMbtiType(e.target.value)}>
          {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>
      {basic && (
        <div className="report-card">
          <h2>기본 리포트</h2>
          <div className="keywords">{basic.keywords?.join(', ')}</div>
          <p><strong>강점:</strong> {basic.strengths}</p>
          <p><strong>약점:</strong> {basic.weaknesses}</p>
          <p><strong>스트레스 반응:</strong> {basic.stress_reaction}</p>
          <p><strong>의사결정 스타일:</strong> {basic.decision_style}</p>
        </div>
      )}
      <div className="report-card ai-section">
        <h2>AI 맞춤 해석</h2>
        <input placeholder="직업" value={job} onChange={(e) => setJob(e.target.value)} />
        <input placeholder="현재 고민" value={concern} onChange={(e) => setConcern(e.target.value)} />
        <input placeholder="관계 고민" value={relConcern} onChange={(e) => setRelConcern(e.target.value)} />
        <button onClick={handleAiReport} disabled={loadingAi}>
          {loadingAi ? '생성 중...' : 'AI 해석 생성'}
        </button>
        {ai && <div className="ai-result">{ai}</div>}
      </div>
    </div>
  )
}
