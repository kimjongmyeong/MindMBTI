import { useState } from 'react'
import { getCompatibility } from '../api'

const TYPES = ['INTJ','INTP','ENTJ','ENTP','INFJ','INFP','ENFJ','ENFP','ISTJ','ISFJ','ESTJ','ESFJ','ISTP','ISFP','ESTP','ESFP']

export default function Compatibility() {
  const [typeA, setTypeA] = useState('ENFP')
  const [typeB, setTypeB] = useState('INTJ')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    setLoading(true)
    setResult(null)
    try {
      const d = await getCompatibility(typeA, typeB)
      setResult(d)
    } catch (e) {
      alert(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page compatibility-page">
      <h1>궁합 분석</h1>
      <div className="compat-form">
        <select value={typeA} onChange={(e) => setTypeA(e.target.value)}>
          {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
        <span>vs</span>
        <select value={typeB} onChange={(e) => setTypeB(e.target.value)}>
          {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
        <button onClick={handleAnalyze} disabled={loading}>
          {loading ? '분석 중...' : '궁합 보기'}
        </button>
      </div>
      {result && (
        <div className="compat-result">
          <h2>관계 유형: {result.relationship_type}</h2>
          <div>
            <h3>갈등 포인트</h3>
            <ul>{result.conflict_points?.map((c, i) => <li key={i}>{c}</li>)}</ul>
          </div>
          <div>
            <h3>의사소통 전략</h3>
            <ul>{result.communication_strategy?.map((s, i) => <li key={i}>{s}</li>)}</ul>
          </div>
          <div>
            <h3>장기 관계 유지 팁</h3>
            <ul>{result.long_term_tips?.map((t, i) => <li key={i}>{t}</li>)}</ul>
          </div>
        </div>
      )}
    </div>
  )
}
