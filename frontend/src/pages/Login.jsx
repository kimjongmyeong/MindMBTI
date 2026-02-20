import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../api'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { access_token } = await login(email, password)
      localStorage.setItem('token', access_token)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="page form-page">
      <h1>로그인</h1>
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
        <button type="submit">로그인</button>
      </form>
      <p><Link to="/register">회원가입</Link></p>
    </div>
  )
}
