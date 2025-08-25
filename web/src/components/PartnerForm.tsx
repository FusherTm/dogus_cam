import React, { useState } from 'react'
import {
  partnerCreateSchema,
  partnerUpdateSchema,
  Partner,
  PartnerCreate,
  PartnerUpdate,
} from '../types/partner'

interface Props {
  mode: 'create' | 'edit'
  initial?: Partner
  onSubmit: (data: PartnerCreate | PartnerUpdate) => void
  onCancel: () => void
  error?: string
}

const PartnerForm: React.FC<Props> = ({ mode, initial, onSubmit, onCancel, error }) => {
  const [form, setForm] = useState({
    name: initial?.name || '',
    type: initial?.type || 'customer',
    email: initial?.email || '',
    phone: initial?.phone || '',
    tax_number: initial?.tax_number || '',
    billing_address: initial?.billing_address || '',
    shipping_address: initial?.shipping_address || '',
    is_active: initial?.is_active ?? true,
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type, checked } = e.target as HTMLInputElement
    setForm((f) => ({ ...f, [name]: type === 'checkbox' ? checked : value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const schema = mode === 'edit' ? partnerUpdateSchema : partnerCreateSchema
    const payload: any = {
      ...form,
      email: form.email === '' ? undefined : form.email,
      phone: form.phone === '' ? undefined : form.phone,
      tax_number: form.tax_number === '' ? undefined : form.tax_number,
      billing_address: form.billing_address === '' ? undefined : form.billing_address,
      shipping_address: form.shipping_address === '' ? undefined : form.shipping_address,
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
        Type
        <select name="type" value={form.type} onChange={handleChange}>
          <option value="customer">Customer</option>
          <option value="supplier">Supplier</option>
          <option value="both">Both</option>
        </select>
        {errors.type && <span style={{ color: 'red' }}>{errors.type}</span>}
      </label>
      <label>
        Email
        <input name="email" value={form.email} onChange={handleChange} />
        {errors.email && <span style={{ color: 'red' }}>{errors.email}</span>}
      </label>
      <label>
        Phone
        <input name="phone" value={form.phone} onChange={handleChange} />
        {errors.phone && <span style={{ color: 'red' }}>{errors.phone}</span>}
      </label>
      <label>
        Tax Number
        <input name="tax_number" value={form.tax_number} onChange={handleChange} />
        {errors.tax_number && <span style={{ color: 'red' }}>{errors.tax_number}</span>}
      </label>
      <label>
        Billing Address
        <input name="billing_address" value={form.billing_address} onChange={handleChange} />
        {errors.billing_address && (
          <span style={{ color: 'red' }}>{errors.billing_address}</span>
        )}
      </label>
      <label>
        Shipping Address
        <input
          name="shipping_address"
          value={form.shipping_address}
          onChange={handleChange}
        />
        {errors.shipping_address && (
          <span style={{ color: 'red' }}>{errors.shipping_address}</span>
        )}
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
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button type="submit">{mode === 'create' ? 'Create' : 'Update'}</button>
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  )
}

export default PartnerForm

