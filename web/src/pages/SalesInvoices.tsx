import React, { useState, useEffect } from 'react'
import { useAuth } from '../store/auth'
import {
  listInvoices,
  createInvoice,
  updateInvoice,
  setInvoiceStatus,
  getInvoice,
  getPartnerBalance,
} from '../lib/invoices'
import { listPartners } from '../lib/partners'
import InvoiceForm from '../components/InvoiceForm'
import StatusBadge from '../components/StatusBadge'
import { Invoice } from '../types/invoice'

const statusOptions: Record<string, string[]> = {
  DRAFT: ['ISSUED', 'CANCELLED'],
  ISSUED: ['PAID', 'CANCELLED'],
  PAID: [],
  CANCELLED: [],
}

const SalesInvoices: React.FC = () => {
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
  const [balancePartner, setBalancePartner] = useState<string | null>(null)

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

  const invoicesQuery = listInvoices({ search, status, partnerId, page, pageSize })
  const partnersQuery = listPartners({ search: partnerSearch, type: '', page: 1, pageSize: 20 })

  useEffect(() => {
    const found = partnersQuery.data?.items.find((p) => p.name === partnerInput)
    setPartnerId(found ? found.id : '')
    setPage(1)
  }, [partnerInput, partnersQuery.data])

  const createMutation = createInvoice()
  const updateMutation = updateInvoice()
  const statusMutation = setInvoiceStatus()

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

  const invoiceDetail = getInvoice(editingId || '')
  const balanceQuery = getPartnerBalance(balancePartner || '')

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
          <option value="ISSUED">ISSUED</option>
          <option value="PAID">PAID</option>
          <option value="CANCELLED">CANCELLED</option>
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
        {isAdmin && <button onClick={openNew}>New Invoice</button>}
      </div>
      {actionError && <div style={{ color: 'red' }}>{actionError}</div>}
      {invoicesQuery.isLoading && <div>Loading...</div>}
      {invoicesQuery.isError && <div>Error loading invoices</div>}
      {!invoicesQuery.isLoading && invoicesQuery.data && (
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
              {invoicesQuery.data.items.map((o: Invoice) => (
                <tr key={o.id}>
                  <td>{o.number}</td>
                  <td>{o.partner_id}</td>
                  <td>
                    <StatusBadge status={o.status} />
                  </td>
                  <td>{o.issue_date}</td>
                  <td>{o.grand_total}</td>
                  <td>
                    <button onClick={() => alert(JSON.stringify(o, null, 2))}>View</button>
                    {isAdmin && o.status === 'DRAFT' && (
                      <button onClick={() => openEdit(o.id)}>Edit</button>
                    )}
                    {isAdmin && statusOptions[o.status].length > 0 && (
                      <select
                        defaultValue=""
                        onChange={(e) => {
                          if (e.target.value) handleStatusChange(o.id, e.target.value)
                        }}
                      >
                        <option value="">Status</option>
                        {statusOptions[o.status].map((s) => (
                          <option key={s} value={s}>
                            {s}
                          </option>
                        ))}
                      </select>
                    )}
                    <button onClick={() => setBalancePartner(o.partner_id)}>View Balance</button>
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
                disabled={page * pageSize >= invoicesQuery.data.total}
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
            <div>Total: {invoicesQuery.data.total}</div>
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
            {editingId && invoiceDetail.isLoading && <div>Loading...</div>}
            {(!editingId || invoiceDetail.data) && (
              <InvoiceForm
                mode={editingId ? 'edit' : 'create'}
                initial={editingId ? invoiceDetail.data : undefined}
                onSubmit={handleSubmit}
                onCancel={() => setShowForm(false)}
                error={formError || undefined}
              />
            )}
          </div>
        </div>
      )}
      {balancePartner && (
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
          onClick={() => setBalancePartner(null)}
        >
          <div style={{ background: '#fff', padding: '1rem' }} onClick={(e) => e.stopPropagation()}>
            {balanceQuery.isLoading && <div>Loading...</div>}
            {balanceQuery.data && (
              <table border={1} cellPadding={4} cellSpacing={0}>
                <thead>
                  <tr>
                    <th>Invoice</th>
                    <th>Issued</th>
                    <th>Allocated</th>
                    <th>Remaining</th>
                  </tr>
                </thead>
                <tbody>
                  {balanceQuery.data.map((b) => (
                    <tr key={b.invoice_no}>
                      <td>{b.invoice_no}</td>
                      <td>{b.issued_total}</td>
                      <td>{b.allocated}</td>
                      <td>{b.remaining}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default SalesInvoices

