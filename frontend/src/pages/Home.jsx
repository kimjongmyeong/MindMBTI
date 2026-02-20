import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="page home">
      <div className="hero">
        <h1>MindMBTI</h1>
        <p>MBTI 기반 심리 분석 서비스</p>
      </div>
      <nav className="nav-cards">
        <Link to="/mbti" className="card-link">MBTI 검사하기</Link>
        <Link to="/report" className="card-link">기본 리포트</Link>
        <Link to="/compatibility" className="card-link">궁합 분석</Link>
        <Link to="/career" className="card-link">직무 매칭</Link>
        <Link to="/dashboard" className="card-link sub">대시보드</Link>
        <Link to="/profile" className="card-link sub">마이페이지</Link>
        <Link to="/login" className="card-link sub">로그인</Link>
        <Link to="/register" className="card-link sub">회원가입</Link>
      </nav>
    </div>
  )
}
