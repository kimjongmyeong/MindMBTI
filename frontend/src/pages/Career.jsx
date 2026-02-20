import { useState, useEffect } from 'react'
import { getCareerMatch, getAiCareerAdvice } from '../api'

const TYPES = ['INTJ','INTP','ENTJ','ENTP','INFJ','INFP','ENFJ','ENFP','ISTJ','ISFJ','ESTJ','ESFJ','ISTP','ISFP','ESTP','ESFP']

export default function Career() {
  const [mbtiType, setMbtiType] = useState('INTJ')
  const [currentJob, setCurrentJob] = useState('')
  const [data, setData] = useState(null)
  const [aiAdvice, setAiAdvice] = useState(null)
  const [loadingAi, setLoadingAi] = useState(false)

  useEffect(() => {
    getCareerMatch(mbtiType).then(setData).catch(console.error)
    setAiAdvice(null)
  }, [mbtiType])

  const handleAiAdvice = async () => {
    if (!currentJob.trim()) return
    setLoadingAi(true)
    setAiAdvice(null)
    try {
      const d = await getAiCareerAdvice(mbtiType, currentJob)
      setAiAdvice(d)
    } catch (e) {
      alert(e.message)
    } finally {
      setLoadingAi(false)
    }
  }

  return (
    <div className="page career-page">
      <h1>직무 매칭</h1>
      <div className="type-select">
        <label>MBTI 유형</label>
        <select value={mbtiType} onChange={(e) => setMbtiType(e.target.value)}>
          {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>
      {data && (
        <div className="career-result">
          <h2>{data.mbti_type} 추천 직무</h2>
          <ul>
            {data.recommended_careers?.map((c, i) => <li key={i}>{c}</li>)}
          </ul>
        </div>
      )}
      <div className="career-ai-section">
        <h2>AI 커리어 조언</h2>
        <input
          placeholder="현재 직무 (예: 소프트웨어 개발자)"
          value={currentJob}
          onChange={(e) => setCurrentJob(e.target.value)}
        />
        <button onClick={handleAiAdvice} disabled={loadingAi || !currentJob.trim()}>
          {loadingAi ? '생성 중...' : '조언 받기'}
        </button>
        {aiAdvice && (
          <div className="ai-advice-result">
            <p><strong>커리어 조언:</strong> {aiAdvice.career_advice}</p>
            <p><strong>강점 활용 전략:</strong> {aiAdvice.strength_strategy}</p>
          </div>
        )}
      </div>
    </div>
  )
}
