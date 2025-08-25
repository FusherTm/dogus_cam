import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './store/auth'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Layout from './components/Layout'
import Products from './pages/Products'
import Partners from './pages/Partners'

const PrivateRoute = ({ children }: { children: JSX.Element }) => {
  const { token } = useAuth()
  return token ? children : <Navigate to="/login" replace />
}

const PublicRoute = ({ children }: { children: JSX.Element }) => {
  const { token } = useAuth()
  return token ? <Navigate to="/dashboard" replace /> : children
}

export const AppRoutes = () => (
  <Routes>
    <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
    <Route
      path="/dashboard"
      element={
        <PrivateRoute>
          <Layout>
            <Dashboard />
          </Layout>
        </PrivateRoute>
      }
    />
    <Route
      path="/products"
      element={
        <PrivateRoute>
          <Layout>
            <Products />
          </Layout>
        </PrivateRoute>
      }
    />
    <Route
      path="/partners"
      element={
        <PrivateRoute>
          <Layout>
            <Partners />
          </Layout>
        </PrivateRoute>
      }
    />
  </Routes>
)
