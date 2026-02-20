import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { getProfile, updateProfile } from '../api'

const GENDERS = [
  { value: '', label: '선택 안 함' },
  { value: 'male', label: '남성' },
  { value: 'female', label: '여성' },
  { value: 'other', label: '기타' },
  { value: 'prefer_not_to_say', label: '비공개' },
]

const AGE_RANGES = [
  { value: '', label: '선택 안 함' },
  { value: '10s', label: '10대' },
  { value: '20s', label: '20대' },
  { value: '30s', label: '30대' },
  { value: '40s', label: '40대' },
  { value: '50s', label: '50대' },
  { value: '60+', label: '60대 이상' },
]

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [nickname, setNickname] = useState('')
  const [gender, setGender] = useState('')
  const [ageRange, setAgeRange] = useState('')
  const [profileImageUrl, setProfileImageUrl] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    getProfile()
      .then((d) => {
        setProfile(d)
        setNickname(d.nickname || '')
        setGender(d.gender || '')
        setAgeRange(d.age_range || '')
        setProfileImageUrl(d.profile_image_url || '')
      })
      .catch((e) => {
        setError(e.message)
        if (e.message?.includes('인증') || e.message?.includes('토큰')) {
          navigate('/login')
        }
      })
      .finally(() => setLoading(false))
  }, [navigate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      const updated = await updateProfile({
        nickname: nickname || undefined,
        gender: gender || undefined,
        age_range: ageRange || undefined,
        profile_image_url: profileImageUrl || undefined,
      })
      setProfile(updated)
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="page"><p>로딩 중...</p></div>
  if (error && !profile) return <div className="page"><p className="error">{error}</p></div>

  return (
    <div className="page form-page">
      <h1>내 프로필</h1>
      {profile?.profile_image_url && (
        <div className="profile-avatar">
          <img src={profile.profile_image_url} alt="프로필" />
        </div>
      )}
      <form onSubmit={handleSubmit} className="form">
        {error && <p className="error">{error}</p>}
        <input
          type="text"
          placeholder="닉네임"
          value={nickname}
          onChange={(e) => setNickname(e.target.value)}
          required
        />
        <select value={gender} onChange={(e) => setGender(e.target.value)}>
          {GENDERS.map((g) => <option key={g.value} value={g.value}>{g.label}</option>)}
        </select>
        <select value={ageRange} onChange={(e) => setAgeRange(e.target.value)}>
          {AGE_RANGES.map((a) => <option key={a.value} value={a.value}>{a.label}</option>)}
        </select>
        <input
          type="url"
          placeholder="프로필 이미지 URL"
          value={profileImageUrl}
          onChange={(e) => setProfileImageUrl(e.target.value)}
        />
        <p className="form-hint">이메일: {profile?.email}</p>
        <button type="submit" disabled={saving}>{saving ? '저장 중...' : '저장'}</button>
      </form>
      <p><Link to="/">홈으로</Link></p>
    </div>
  )
}
