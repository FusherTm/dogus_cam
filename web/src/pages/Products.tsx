import React, { useState, useEffect } from 'react'
import { useAuth } from '../store/auth'
import {
  listProducts,
  createProduct,
  updateProduct,
  deleteProduct,
} from '../lib/products'
import { Product, ProductCreate, ProductUpdate } from '../types/product'
import ProductForm from '../components/ProductForm'
import ConfirmDialog from '../components/ConfirmDialog'

const Products: React.FC = () => {
  const { currentUser } = useAuth()
  const isAdmin = currentUser?.role === 'admin'

  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Product | null>(null)
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    const t = setTimeout(() => {
      setSearch(searchInput)
      setPage(1)
    }, 300)
    return () => clearTimeout(t)
  }, [searchInput])

  const { data, isLoading, isError } = listProducts({
    search,
    page,
    pageSize,
  })

  const createMutation = createProduct()
  const updateMutation = editing ? updateProduct(editing.id) : null
  const deleteMutation = deleteProduct()

  const openNew = () => {
    setEditing(null)
    setFormError(null)
    setShowForm(true)
  }

  const openEdit = (p: Product) => {
    setEditing(p)
    setFormError(null)
    setShowForm(true)
  }

  const handleSubmit = async (payload: ProductCreate | ProductUpdate) => {
    try {
      if (editing) {
        await updateMutation!.mutateAsync(payload as ProductUpdate)
      } else {
        await createMutation.mutateAsync(payload as ProductCreate)
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
        <input
          placeholder="Search"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />
        {isAdmin && <button onClick={openNew}>New Product</button>}
      </div>
      {isLoading && <div>Loading...</div>}
      {isError && <div>Error loading products</div>}
      {!isLoading && data && (
        <>
          <table border={1} cellPadding={4} cellSpacing={0} style={{ width: '100%' }}>
            <thead>
              <tr>
                <th>Name</th>
                <th>SKU</th>
                <th>Price</th>
                <th>Active</th>
                <th>Restock Level</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((p: Product) => (
                <tr key={p.id}>
                  <td>{p.name}</td>
                  <td>{p.sku}</td>
                  <td>{p.price}</td>
                  <td>{p.is_active ? 'Yes' : 'No'}</td>
                  <td>{p.restock_level ?? '-'}</td>
                  <td>{p.created_at_utc}</td>
                  <td>
                    <button onClick={() => alert(JSON.stringify(p, null, 2))}>View</button>
                    {isAdmin && (
                      <>
                        <button onClick={() => openEdit(p)}>Edit</button>
                        <ConfirmDialog
                          message="Delete this product?"
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
            <ProductForm
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

export default Products

