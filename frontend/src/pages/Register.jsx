import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register } from '../api'

export default function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [nickname, setNickname] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await register(email, password, nickname)
      navigate('/login')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="page form-page">
      <h1>회원가입</h1>
      <form onSubmit={handleSubmit} className="form">
        {error && <p className="error">{error}</p>}
        <input
          type="email"
          placeholder="이메일"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="비밀번호"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="닉네임"
          value={nickname}
          onChange={(e) => setNickname(e.target.value)}
          required
        />
        <button type="submit">가입하기</button>
      </form>
      <p><Link to="/login">로그인</Link></p>
    </div>
  )
}
