import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import './App.css'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import MbtiTest from './pages/MbtiTest'
import Result from './pages/Result'
import Report from './pages/Report'
import Compatibility from './pages/Compatibility'
import Career from './pages/Career'
import Profile from './pages/Profile'
import Share from './pages/Share'
import Dashboard from './pages/Dashboard'

function Layout({ children }) {
  return (
    <div className="app">
      <header className="header">
        <Link to="/" className="logo">MindMBTI</Link>
        <nav>
          <Link to="/mbti">검사</Link>
          <Link to="/report">리포트</Link>
          <Link to="/compatibility">궁합</Link>
          <Link to="/career">직무</Link>
          <Link to="/dashboard">대시보드</Link>
          <Link to="/profile">마이페이지</Link>
          <Link to="/login">로그인</Link>
        </nav>
      </header>
      <main className="main">{children}</main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/mbti" element={<MbtiTest />} />
          <Route path="/result/:sessionId" element={<Result />} />
          <Route path="/report" element={<Report />} />
          <Route path="/compatibility" element={<Compatibility />} />
          <Route path="/career" element={<Career />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/share/:shareId" element={<Share />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
