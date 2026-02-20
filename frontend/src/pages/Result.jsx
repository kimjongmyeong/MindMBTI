import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getResult, createShare, saveToHistory } from '../api'

const API = '/api'

export default function Result() {
  const { sessionId } = useParams()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [shareUrl, setShareUrl] = useState('')
  const [sharing, setSharing] = useState(false)
  const [saved, setSaved] = useState(false)
  const [saving, setSaving] = useState(false)
  const [hasToken, setHasToken] = useState(false)

  useEffect(() => {
    setHasToken(!!localStorage.getItem('token'))
    getResult(sessionId).then(setData).catch((e) => setError(e.message))
  }, [sessionId])

  const handleSave = async () => {
    setSaving(true)
    try {
      await saveToHistory(sessionId)
      setSaved(true)
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const handleShare = async () => {
    setSharing(true)
    try {
      const { share_id } = await createShare(sessionId)
      const url = `${window.location.origin}/share/${share_id}`
      setShareUrl(url)
      await navigator.clipboard?.writeText(url)
    } catch (e) {
      setError(e.message)
    } finally {
      setSharing(false)
    }
  }

  const pdfUrl = `${API}/mbti/result/${sessionId}/pdf`

  if (error) return <div className="page"><p className="error">{error}</p></div>
  if (!data) return <div className="page"><p>로딩 중...</p></div>

  return (
    <div className="page result-page">
      <h1>MBTI 결과</h1>
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
      <div className="result-actions">
        {hasToken && (
          <button onClick={handleSave} disabled={saving || saved} className="btn">
            {saved ? '저장됨' : saving ? '저장 중...' : '기록에 저장'}
          </button>
        )}
        <a href={pdfUrl} download target="_blank" rel="noreferrer" className="btn">
          PDF 다운로드
        </a>
        <button onClick={handleShare} disabled={sharing} className="btn">
          {sharing ? '처리 중...' : '공유 링크 만들기'}
        </button>
        {shareUrl && <p className="share-url">링크가 복사되었습니다: {shareUrl}</p>}
      </div>
      <div className="actions">
        <Link to={`/report?type=${data.type}`}>기본 리포트 보기</Link>
        <Link to="/mbti">다시 검사하기</Link>
        <Link to="/">홈</Link>
      </div>
    </div>
  )
}
