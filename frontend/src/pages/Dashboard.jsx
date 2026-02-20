import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend } from 'recharts'
import { getHistory, compareResults } from '../api'

export default function Dashboard() {
  const [history, setHistory] = useState([])
  const [compareData, setCompareData] = useState(null)
  const [sessionA, setSessionA] = useState('')
  const [sessionB, setSessionB] = useState('')
  const [loading, setLoading] = useState(true)
  const [comparing, setComparing] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    getHistory()
      .then((d) => setHistory(d.history || []))
      .catch(() => navigate('/login'))
      .finally(() => setLoading(false))
  }, [navigate])

  const handleCompare = async () => {
    if (!sessionA || !sessionB) return
    setComparing(true)
    setCompareData(null)
    try {
      const d = await compareResults(sessionA, sessionB)
      setCompareData(d)
    } catch (e) {
      alert(e.message)
    } finally {
      setComparing(false)
    }
  }

  if (loading) return <div className="page"><p>로딩 중...</p></div>

  return (
    <div className="page dashboard-page">
      <h1>내 분석 기록</h1>
      {history.length === 0 ? (
        <p className="empty-msg">저장된 검사 결과가 없습니다. <Link to="/mbti">검사하기</Link> → 결과 페이지에서 "기록에 저장" 버튼을 눌러보세요.</p>
      ) : (
        <>
          <div className="history-list">
            {history.map((r, i) => (
              <div key={r.session_id} className="history-item">
                <span className="type">{r.type}</span>
                <span className="date">{new Date(r.created_at).toLocaleDateString('ko-KR')}</span>
                <Link to={`/result/${r.session_id}`}>보기</Link>
              </div>
            ))}
          </div>
          {history.length >= 2 && (
            <div className="compare-section">
              <h2>재검사 비교</h2>
              <div className="compare-form">
                <select value={sessionA} onChange={(e) => setSessionA(e.target.value)}>
                  <option value="">결과 A 선택</option>
                  {history.map((r) => (
                    <option key={r.session_id} value={r.session_id}>
                      {r.type} ({r.created_at.slice(0, 10)})
                    </option>
                  ))}
                </select>
                <span>vs</span>
                <select value={sessionB} onChange={(e) => setSessionB(e.target.value)}>
                  <option value="">결과 B 선택</option>
                  {history.map((r) => (
                    <option key={r.session_id} value={r.session_id}>
                      {r.type} ({r.created_at.slice(0, 10)})
                    </option>
                  ))}
                </select>
                <button onClick={handleCompare} disabled={comparing || !sessionA || !sessionB}>
                  {comparing ? '비교 중...' : '비교하기'}
                </button>
              </div>
              {compareData && (
                <div className="compare-result">
                  <p><strong>유형 변화:</strong> {compareData.result_a.type} → {compareData.result_b.type} {compareData.type_changed && '(변화 있음)'}</p>
                  <div className="radar-chart-wrap">
                    <ResponsiveContainer width="100%" height={280}>
                      <RadarChart
                        data={compareData.dimension_changes?.map((d) => {
                          const first = d.dimension?.[0] ?? 'E'
                          return {
                            subject: d.dimension,
                            A: d.before?.[first] ?? 50,
                            B: d.after?.[first] ?? 50,
                            fullMark: 100,
                          }
                        }) ?? []}
                      >
                        <PolarGrid />
                        <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                        <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#94a3b8' }} />
                        <Radar name={`${compareData.result_a.type} (이전)`} dataKey="A" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
                        <Radar name={`${compareData.result_b.type} (이후)`} dataKey="B" stroke="#22c55e" fill="#22c55e" fillOpacity={0.3} />
                        <Legend />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="dim-changes">
                    {compareData.dimension_changes?.map((d) => (
                      <div key={d.dimension}>
                        {d.dimension}: {d.change >= 0 ? '+' : ''}{d.change}%p
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
      <p><Link to="/">홈</Link></p>
    </div>
  )
}
