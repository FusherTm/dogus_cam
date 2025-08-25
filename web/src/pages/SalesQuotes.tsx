import React, { useState, useEffect } from 'react'
import { useAuth } from '../store/auth'
import {
  listQuotes,
  createQuote,
  updateQuote,
  setQuoteStatus,
  convertQuoteToOrder,
  getQuote,
} from '../lib/quotes'
import { listPartners } from '../lib/partners'
import QuoteForm from '../components/QuoteForm'
import StatusBadge from '../components/StatusBadge'
import { Quote } from '../types/quote'

const statusOptions: Record<string, string[]> = {
  DRAFT: ['SENT'],
  SENT: ['APPROVED', 'REJECTED', 'EXPIRED'],
  APPROVED: ['REJECTED', 'EXPIRED'],
  REJECTED: [],
  EXPIRED: [],
}

const SalesQuotes: React.FC = () => {
  const { currentUser } = useAuth()
  const isAdmin = currentUser?.role === 'admin'

  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [partnerInput, setPartnerInput] = useState('')
  const [partnerSearch, setPartnerSearch] = useState('')
  const [partnerId, setPartnerId] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formError, setFormError] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  useEffect(() => {
    const t = setTimeout(() => {
      setSearch(searchInput)
      setPage(1)
    }, 300)
    return () => clearTimeout(t)
  }, [searchInput])

  useEffect(() => {
    const t = setTimeout(() => setPartnerSearch(partnerInput), 300)
    return () => clearTimeout(t)
  }, [partnerInput])

  const quotesQuery = listQuotes({ search, status, partnerId, page, pageSize })
  const partnersQuery = listPartners({ search: partnerSearch, type: '', page: 1, pageSize: 20 })

  useEffect(() => {
    const found = partnersQuery.data?.items.find((p) => p.name === partnerInput)
    setPartnerId(found ? found.id : '')
    setPage(1)
  }, [partnerInput, partnersQuery.data])

  const createMutation = createQuote()
  const updateMutation = updateQuote()
  const statusMutation = setQuoteStatus()
  const convertMutation = convertQuoteToOrder()

  const openNew = () => {
    setEditingId(null)
    setFormError(null)
    setShowForm(true)
  }

  const openEdit = (id: string) => {
    setEditingId(id)
    setFormError(null)
    setShowForm(true)
  }

  const handleSubmit = async (payload: any) => {
    try {
      if (editingId) {
        await updateMutation.mutateAsync({ id: editingId, payload })
      } else {
        await createMutation.mutateAsync(payload)
      }
      setShowForm(false)
    } catch (err: any) {
      setFormError(err.response?.data?.detail || 'Error')
    }
  }

  const handleStatusChange = async (id: string, newStatus: string) => {
    try {
      await statusMutation.mutateAsync({ id, status: newStatus })
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'Error')
    }
  }

  const handleConvert = async (id: string) => {
    try {
      const res = await convertMutation.mutateAsync(id)
      alert(`Converted to order: ${res.id}`)
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'Error')
    }
  }

  const quoteDetail = getQuote(editingId || '')

  return (
    <div style={{ padding: '1rem' }}>
      <div
        style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', gap: '0.5rem' }}
      >
        <input
          placeholder="Search"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />
        <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1) }}>
          <option value="">All</option>
          <option value="DRAFT">DRAFT</option>
          <option value="SENT">SENT</option>
          <option value="APPROVED">APPROVED</option>
          <option value="REJECTED">REJECTED</option>
          <option value="EXPIRED">EXPIRED</option>
        </select>
        <input
          list="partner-options"
          placeholder="Partner"
          value={partnerInput}
          onChange={(e) => setPartnerInput(e.target.value)}
        />
        <datalist id="partner-options">
          {partnersQuery.data?.items.map((p) => (
            <option key={p.id} value={p.name} />
          ))}
        </datalist>
        {isAdmin && <button onClick={openNew}>New Quote</button>}
      </div>
      {actionError && <div style={{ color: 'red' }}>{actionError}</div>}
      {quotesQuery.isLoading && <div>Loading...</div>}
      {quotesQuery.isError && <div>Error loading quotes</div>}
      {!quotesQuery.isLoading && quotesQuery.data && (
        <>
          <table border={1} cellPadding={4} cellSpacing={0} style={{ width: '100%' }}>
            <thead>
              <tr>
                <th>Number</th>
                <th>Partner</th>
                <th>Status</th>
                <th>Issue Date</th>
                <th>Grand Total</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {quotesQuery.data.items.map((q: Quote) => (
                <tr key={q.id}>
                  <td>{q.number}</td>
                  <td>{q.partner_id}</td>
                  <td>
                    <StatusBadge status={q.status} />
                  </td>
                  <td>{q.issue_date}</td>
                  <td>{q.grand_total}</td>
                  <td>
                    <button onClick={() => alert(JSON.stringify(q, null, 2))}>View</button>
                    {isAdmin && q.status === 'DRAFT' && (
                      <button onClick={() => openEdit(q.id)}>Edit</button>
                    )}
                    {isAdmin && statusOptions[q.status].length > 0 && (
                      <select
                        defaultValue=""
                        onChange={(e) => {
                          if (e.target.value) handleStatusChange(q.id, e.target.value)
                        }}
                      >
                        <option value="">Status</option>
                        {statusOptions[q.status].map((s) => (
                          <option key={s} value={s}>
                            {s}
                          </option>
                        ))}
                      </select>
                    )}
                    {isAdmin && ['APPROVED', 'SENT'].includes(q.status) && (
                      <button onClick={() => handleConvert(q.id)}>To Order</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginTop: '1rem',
            }}
          >
            <div>
              <button disabled={page === 1} onClick={() => setPage((p) => p - 1)}>
                Prev
              </button>
              <span style={{ margin: '0 0.5rem' }}>{page}</span>
              <button
                disabled={page * pageSize >= quotesQuery.data.total}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
            <div>
              <select
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value))
                  setPage(1)
                }}
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </div>
            <div>Total: {quotesQuery.data.total}</div>
          </div>
        </>
      )}
      {showForm && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.3)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <div style={{ background: '#fff', padding: '1rem', minWidth: 400 }}>
            {editingId && quoteDetail.isLoading && <div>Loading...</div>}
            {(!editingId || quoteDetail.data) && (
              <QuoteForm
                mode={editingId ? 'edit' : 'create'}
                initial={editingId ? quoteDetail.data : undefined}
                onSubmit={handleSubmit}
                onCancel={() => setShowForm(false)}
                error={formError || undefined}
              />
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default SalesQuotes

