import React from 'react'

const colors: Record<string, string> = {
  // quote statuses
  DRAFT: '#999',
  SENT: '#0af',
  APPROVED: 'green',
  REJECTED: 'red',
  EXPIRED: 'orange',
  // order statuses
  NEW: '#999',
  CONFIRMED: '#0af',
  FULFILLED: 'green',
  CANCELLED: 'red',
}

const StatusBadge: React.FC<{ status: string }> = ({ status }) => (
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

