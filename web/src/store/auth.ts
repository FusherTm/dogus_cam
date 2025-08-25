import React, { createContext, useContext, useState } from 'react'
import api from '../lib/api'

interface User {
  id: string
  email: string
  role: string
}

interface AuthContextProps {
  token: string | null
  currentUser: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchMe: () => Promise<void>
}

const AuthContext = createContext<AuthContextProps>({} as AuthContextProps)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [currentUser, setCurrentUser] = useState<User | null>(null)

  const fetchMe = async () => {
    const res = await api.get('/auth/me')
    setCurrentUser(res.data)
  }

  const login = async (email: string, password: string) => {
    const res = await api.post('/auth/login', { email, password })
    const t = res.data.token || res.data.access_token
    localStorage.setItem('token', t)
    setToken(t)
    await fetchMe()
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setCurrentUser(null)
  }

  return (
    <AuthContext.Provider value={{ token, currentUser, login, logout, fetchMe }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
