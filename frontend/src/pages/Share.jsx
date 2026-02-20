import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getShare } from '../api'

const API = '/api'

export default function Share() {
  const { shareId } = useParams()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getShare(shareId).then(setData).catch((e) => setError(e.message))
  }, [shareId])

  if (error) return <div className="page"><p className="error">{error}</p></div>
  if (!data) return <div className="page"><p>로딩 중...</p></div>

  const pdfUrl = `${API}/share/${shareId}/pdf`

  return (
    <div className="page result-page">
      <h1>공유된 MBTI 결과</h1>
      <div className="result-type">{data.type}</div>
      {data.percentages && (
        <div className="percentages">
          {Object.entries(data.percentages).map(([dim, pct]) => (
            <div key={dim} className="dim-row">
              <span>{dim}:</span>
              <span>{pct[dim[0]]}% / {pct[dim[2]]}%</span>
            </div>
          ))}
        </div>
      )}
      {data.report?.keywords && (
        <div className="report-preview">
          <p><strong>키워드:</strong> {data.report.keywords.join(', ')}</p>
        </div>
      )}
      <div className="result-actions">
        <a href={pdfUrl} download target="_blank" rel="noreferrer" className="btn">
          PDF 다운로드
        </a>
      </div>
      <p><Link to="/">MindMBTI 홈</Link></p>
    </div>
  )
}
