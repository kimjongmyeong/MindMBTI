// 프로덕션: VITE_API_URL (예: https://mindmbti-api.onrender.com)
// 로컬: /api (Vite 프록시)
const API = import.meta.env.VITE_API_URL || '/api'

function authHeaders() {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function health() {
  const r = await fetch(`${API}/health`)
  return r.json()
}

export async function register(email, password, nickname) {
  const r = await fetch(`${API}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, nickname }),
  })
  if (!r.ok) {
    const d = await r.json().catch(() => ({}))
    throw new Error(d.detail || '회원가입 실패')
  }
  return r.json()
}

export async function login(email, password) {
  const r = await fetch(`${API}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!r.ok) {
    const d = await r.json().catch(() => ({}))
    throw new Error(d.detail || '로그인 실패')
  }
  return r.json()
}

export async function getQuestions() {
  const r = await fetch(`${API}/mbti/questions`)
  return (await r.json()).questions
}

export async function submitAnswers(answers, sessionId = null) {
  const r = await fetch(`${API}/mbti/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answers, session_id: sessionId }),
  })
  return r.json()
}

export async function getResult(sessionId) {
  const r = await fetch(`${API}/mbti/result/${sessionId}`)
  if (!r.ok) throw new Error('결과를 불러올 수 없습니다')
  return r.json()
}

export async function getBasicReport(mbtiType) {
  const r = await fetch(`${API}/report/basic/${mbtiType}`)
  if (!r.ok) throw new Error('리포트를 불러올 수 없습니다')
  return r.json()
}

export async function getAiReport(mbtiType, job, currentConcern, relationshipConcern) {
  const r = await fetch(`${API}/report/ai`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mbti_type: mbtiType,
      job: job || undefined,
      current_concern: currentConcern || undefined,
      relationship_concern: relationshipConcern || undefined,
    }),
  })
  if (!r.ok) {
    const d = await r.json().catch(() => ({}))
    throw new Error(d.detail || 'AI 리포트 생성 실패')
  }
  return r.json()
}

export async function getCompatibility(typeA, typeB) {
  const r = await fetch(`${API}/compatibility`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type_a: typeA, type_b: typeB }),
  })
  if (!r.ok) throw new Error('궁합 분석 실패')
  return r.json()
}

export async function getCareerMatch(mbtiType) {
  const r = await fetch(`${API}/career/match/${mbtiType}`)
  if (!r.ok) throw new Error('직무 매칭 실패')
  return r.json()
}

export async function getAiCareerAdvice(mbtiType, currentJob) {
  const r = await fetch(`${API}/career/ai-advice`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mbti_type: mbtiType, current_job: currentJob }),
  })
  if (!r.ok) {
    const d = await r.json().catch(() => ({}))
    throw new Error(d.detail || 'AI 커리어 조언 생성 실패')
  }
  return r.json()
}

export async function createShare(sessionId) {
  const r = await fetch(`${API}/share`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  })
  if (!r.ok) {
    const d = await r.json().catch(() => ({}))
    throw new Error(d.detail || '공유 생성 실패')
  }
  return r.json()
}

export async function getShare(shareId) {
  const r = await fetch(`${API}/share/${shareId}`)
  if (!r.ok) throw new Error('공유된 결과를 불러올 수 없습니다')
  return r.json()
}

export async function getProfile() {
  const r = await fetch(`${API}/user/me`, { headers: authHeaders() })
  if (!r.ok) {
    const d = await r.json().catch(() => ({}))
    throw new Error(d.detail || '프로필 조회 실패')
  }
  return r.json()
}

export async function saveToHistory(sessionId) {
  const r = await fetch(`${API}/dashboard/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ session_id: sessionId }),
  })
  if (!r.ok) {
    const d = await r.json().catch(() => ({}))
    throw new Error(d.detail || '저장 실패')
  }
  return r.json()
}

export async function getHistory() {
  const r = await fetch(`${API}/dashboard/history`, { headers: authHeaders() })
  if (!r.ok) throw new Error('기록 조회 실패')
  return r.json()
}

export async function compareResults(sessionA, sessionB) {
  const r = await fetch(
    `${API}/dashboard/compare?session_a=${encodeURIComponent(sessionA)}&session_b=${encodeURIComponent(sessionB)}`,
    { headers: authHeaders() }
  )
  if (!r.ok) {
    const d = await r.json().catch(() => ({}))
    throw new Error(d.detail || '비교 실패')
  }
  return r.json()
}

export async function updateProfile(data) {
  const r = await fetch(`${API}/user/me`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(data),
  })
  if (!r.ok) {
    const d = await r.json().catch(() => ({}))
    throw new Error(d.detail || '프로필 수정 실패')
  }
  return r.json()
}
