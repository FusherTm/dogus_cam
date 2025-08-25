import React from 'react'

interface Props {
  message: string
  onConfirm: () => void
  children: React.ReactNode
  onCancel?: () => void
}

const ConfirmDialog: React.FC<Props> = ({ message, onConfirm, onCancel, children }) => {
  const handleClick = () => {
    if (window.confirm(message)) {
      onConfirm()
    } else {
      onCancel && onCancel()
    }
  }
  return <span onClick={handleClick}>{children}</span>
}

export default ConfirmDialog

