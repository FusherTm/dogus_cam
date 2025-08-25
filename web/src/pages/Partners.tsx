import React, { useState, useEffect } from 'react'
import { useAuth } from '../store/auth'
import {
  listPartners,
  createPartner,
  updatePartner,
  deletePartner,
} from '../lib/partners'
import { Partner, PartnerCreate, PartnerUpdate } from '../types/partner'
import PartnerForm from '../components/PartnerForm'
import ConfirmDialog from '../components/ConfirmDialog'

const Partners: React.FC = () => {
  const { currentUser } = useAuth()
  const isAdmin = currentUser?.role === 'admin'

  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [type, setType] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Partner | null>(null)
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    const t = setTimeout(() => {
      setSearch(searchInput)
      setPage(1)
    }, 300)
    return () => clearTimeout(t)
  }, [searchInput])

  const { data, isLoading, isError } = listPartners({ search, type, page, pageSize })

  const createMutation = createPartner()
  const updateMutation = editing ? updatePartner(editing.id) : null
  const deleteMutation = deletePartner()

  const openNew = () => {
    setEditing(null)
    setFormError(null)
    setShowForm(true)
  }

  const openEdit = (p: Partner) => {
    setEditing(p)
    setFormError(null)
    setShowForm(true)
  }

  const handleSubmit = async (payload: PartnerCreate | PartnerUpdate) => {
    try {
      if (editing) {
        await updateMutation!.mutateAsync(payload as PartnerUpdate)
      } else {
        await createMutation.mutateAsync(payload as PartnerCreate)
      }
      setShowForm(false)
    } catch (err: any) {
      setFormError(err.response?.data?.detail || 'Error')
    }
  }

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id)
  }

  return (
    <div style={{ padding: '1rem' }}>
      <div
        style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}
      >
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            placeholder="Search"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
          <select
            value={type}
            onChange={(e) => {
              setType(e.target.value)
              setPage(1)
            }}
          >
            <option value="">All</option>
            <option value="customer">Customer</option>
            <option value="supplier">Supplier</option>
            <option value="both">Both</option>
          </select>
        </div>
        {isAdmin && <button onClick={openNew}>New Partner</button>}
      </div>
      {isLoading && <div>Loading...</div>}
      {isError && <div>Error loading partners</div>}
      {!isLoading && data && (
        <>
          <table border={1} cellPadding={4} cellSpacing={0} style={{ width: '100%' }}>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Tax Number</th>
                <th>Active</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((p: Partner) => (
                <tr key={p.id}>
                  <td>{p.name}</td>
                  <td>{p.type}</td>
                  <td>{p.email ?? '-'}</td>
                  <td>{p.phone ?? '-'}</td>
                  <td>{p.tax_number ?? '-'}</td>
                  <td>{p.is_active ? 'Yes' : 'No'}</td>
                  <td>{p.created_at_utc}</td>
                  <td>
                    <button onClick={() => alert(JSON.stringify(p, null, 2))}>View</button>
                    {isAdmin && (
                      <>
                        <button onClick={() => openEdit(p)}>Edit</button>
                        <ConfirmDialog
                          message="Delete this partner?"
                          onConfirm={() => handleDelete(p.id)}
                        >
                          <button>Delete</button>
                        </ConfirmDialog>
                      </>
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
                disabled={page * pageSize >= data.total}
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
            <div>Total: {data.total}</div>
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
          <div style={{ background: '#fff', padding: '1rem', minWidth: 300 }}>
            <PartnerForm
              mode={editing ? 'edit' : 'create'}
              initial={editing || undefined}
              onSubmit={handleSubmit}
              onCancel={() => setShowForm(false)}
              error={formError || undefined}
            />
          </div>
        </div>
      )}
    </div>
  )
}

export default Partners

