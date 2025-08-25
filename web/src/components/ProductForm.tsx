import React, { useState } from 'react'
import {
  productCreateSchema,
  productUpdateSchema,
  Product,
  ProductCreate,
  ProductUpdate,
} from '../types/product'

interface Props {
  mode: 'create' | 'edit'
  initial?: Product
  onSubmit: (data: ProductCreate | ProductUpdate) => void
  onCancel: () => void
  error?: string
}

const ProductForm: React.FC<Props> = ({ mode, initial, onSubmit, onCancel, error }) => {
  const [form, setForm] = useState({
    name: initial?.name || '',
    sku: initial?.sku || '',
    price: initial?.price ?? 0,
    is_active: initial?.is_active ?? true,
    restock_level: initial?.restock_level ?? '',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setForm((f) => ({ ...f, [name]: type === 'checkbox' ? checked : value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const schema = mode === 'edit' ? productUpdateSchema : productCreateSchema
    const payload: any = {
      ...form,
      price: Number(form.price),
      restock_level:
        form.restock_level === '' ? undefined : Number(form.restock_level),
    }
    const parsed = schema.safeParse(payload)
    if (!parsed.success) {
      const errs: Record<string, string> = {}
      parsed.error.errors.forEach((er) => {
        const key = er.path[0] as string
        errs[key] = er.message
      })
      setErrors(errs)
      return
    }
    setErrors({})
    onSubmit(parsed.data)
  }

  return (
    <form
      onSubmit={handleSubmit}
      style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}
    >
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <label>
        Name
        <input name="name" value={form.name} onChange={handleChange} />
        {errors.name && <span style={{ color: 'red' }}>{errors.name}</span>}
      </label>
      <label>
        SKU
        <input name="sku" value={form.sku} onChange={handleChange} />
        {errors.sku && <span style={{ color: 'red' }}>{errors.sku}</span>}
      </label>
      <label>
        Price
        <input
          name="price"
          type="number"
          value={form.price}
          onChange={handleChange}
        />
        {errors.price && <span style={{ color: 'red' }}>{errors.price}</span>}
      </label>
      <label>
        Is Active
        <input
          name="is_active"
          type="checkbox"
          checked={form.is_active}
          onChange={handleChange}
        />
      </label>
      <label>
        Restock Level
        <input
          name="restock_level"
          type="number"
          value={form.restock_level}
          onChange={handleChange}
        />
        {errors.restock_level && (
          <span style={{ color: 'red' }}>{errors.restock_level}</span>
        )}
      </label>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button type="submit">{mode === 'create' ? 'Create' : 'Update'}</button>
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  )
}

export default ProductForm

