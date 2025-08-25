import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../store/auth'

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div style={{ display: 'flex', width: '100%' }}>
      <aside style={{ width: 200, borderRight: '1px solid #ccc', padding: '1rem' }}>
        <h2>DogusCam</h2>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <NavLink to="/dashboard">Dashboard</NavLink>
          <NavLink to="/products">Products</NavLink>
          <NavLink to="/partners">Partners</NavLink>
          <NavLink to="/sales/orders">Sales &gt; Orders</NavLink>
          <NavLink to="/sales/quotes">Sales &gt; Quotes</NavLink>
          <NavLink to="/sales/invoices">Sales &gt; Invoices</NavLink>
        </nav>
      </aside>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <header
          style={{
            borderBottom: '1px solid #ccc',
            padding: '0.5rem 1rem',
            display: 'flex',
            justifyContent: 'space-between',
          }}
        >
          <span>Admin Panel</span>
          <button onClick={handleLogout}>Logout</button>
        </header>
        <main style={{ flex: 1 }}>{children}</main>
      </div>
    </div>
  )
}

export default Layout
