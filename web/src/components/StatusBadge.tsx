import React from 'react'
import { Quote } from '../types/quote'

const colors: Record<Quote['status'], string> = {
  DRAFT: '#999',
  SENT: '#0af',
  APPROVED: 'green',
  REJECTED: 'red',
  EXPIRED: 'orange',
}

const StatusBadge: React.FC<{ status: Quote['status'] }> = ({ status }) => (
  <span
    style={{
      padding: '0.2rem 0.5rem',
      borderRadius: 4,
      background: colors[status],
      color: '#fff',
      fontSize: '0.8rem',
    }}
  >
    {status}
  </span>
)

export default StatusBadge

