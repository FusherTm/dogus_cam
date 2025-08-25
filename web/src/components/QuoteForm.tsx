import React, { useState } from 'react'
import {
  quoteCreateSchema,
  quoteUpdateSchema,
  QuoteDetail,
  QuoteCreate,
  QuoteUpdate,
  QuoteItemIn,
} from '../types/quote'
import { listPartners } from '../lib/partners'
import { listProducts } from '../lib/products'

interface Props {
  mode: 'create' | 'edit'
  initial?: QuoteDetail
  onSubmit: (data: QuoteCreate | QuoteUpdate) => void
  onCancel: () => void
  error?: string
}

const emptyItem: QuoteItemIn = {
  product_id: '',
  description: '',
  quantity: 1,
  unit_price: 0,
  line_discount_rate: 0,
  tax_rate: 0,
}

const QuoteForm: React.FC<Props> = ({ mode, initial, onSubmit, onCancel, error }) => {
  const [form, setForm] = useState({
    partner_id: initial?.partner_id || '',
    currency: initial?.currency || 'USD',
    issue_date: initial?.issue_date || new Date().toISOString().slice(0, 10),
    valid_until: initial?.valid_until || '',
    notes: initial?.notes || '',
    discount_rate: initial?.discount_rate ?? 0,
    items:
      initial?.items?.map((i) => ({
        product_id: i.product_id,
        description: i.description || '',
        quantity: i.quantity,
        unit_price: i.unit_price,
        line_discount_rate: i.line_discount_rate || 0,
        tax_rate: i.tax_rate || 0,
      })) || [emptyItem],
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const partnersQuery = listPartners({ search: '', type: '', page: 1, pageSize: 50 })
  const productsQuery = listProducts({ search: '', page: 1, pageSize: 50 })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
  }

  const handleItemChange = (
    index: number,
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setForm((f) => {
      const items = [...f.items]
      ;(items[index] as any)[name] = value
      return { ...f, items }
    })
  }

  const addItem = () => {
    setForm((f) => ({ ...f, items: [...f.items, { ...emptyItem }] }))
  }

  const removeItem = (idx: number) => {
    setForm((f) => ({ ...f, items: f.items.filter((_, i) => i !== idx) }))
  }

  const calcLine = (item: QuoteItemIn) => {
    const qty = Number(item.quantity) || 0
    const price = Number(item.unit_price) || 0
    const ldisc = Number(item.line_discount_rate) || 0
    const tax = Number(item.tax_rate) || 0
    const lineSubtotal = qty * price * (1 - ldisc / 100)
    const lineTax = lineSubtotal * (tax / 100)
    const lineTotal = lineSubtotal + lineTax
    return { lineSubtotal, lineTax, lineTotal }
  }

  const totals = form.items.reduce(
    (acc, it) => {
      const { lineSubtotal, lineTax } = calcLine(it)
      acc.subtotal += lineSubtotal
      acc.tax_total += lineTax
      return acc
    },
    { subtotal: 0, tax_total: 0 }
  )
  const discounted = totals.subtotal * (1 - Number(form.discount_rate || 0) / 100)
  const grand = discounted + totals.tax_total

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const schema = mode === 'edit' ? quoteUpdateSchema : quoteCreateSchema
    const payload = {
      ...form,
      discount_rate: Number(form.discount_rate) || 0,
      items: form.items.map((it) => ({
        ...it,
        quantity: Number(it.quantity),
        unit_price: Number(it.unit_price),
        line_discount_rate: it.line_discount_rate ? Number(it.line_discount_rate) : undefined,
        tax_rate: it.tax_rate ? Number(it.tax_rate) : undefined,
      })),
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
      style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '80vh', overflowY: 'auto' }}
    >
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <label>
        Partner
        <select name="partner_id" value={form.partner_id} onChange={handleChange}>
          <option value="">Select...</option>
          {partnersQuery.data?.items.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        {errors.partner_id && <span style={{ color: 'red' }}>{errors.partner_id}</span>}
      </label>
      <label>
        Currency
        <select name="currency" value={form.currency} onChange={handleChange}>
          <option value="USD">USD</option>
          <option value="EUR">EUR</option>
          <option value="TRY">TRY</option>
        </select>
      </label>
      <label>
        Issue Date
        <input name="issue_date" type="date" value={form.issue_date} onChange={handleChange} />
        {errors.issue_date && <span style={{ color: 'red' }}>{errors.issue_date}</span>}
      </label>
      <label>
        Valid Until
        <input name="valid_until" type="date" value={form.valid_until} onChange={handleChange} />
      </label>
      <label>
        Notes
        <input name="notes" value={form.notes} onChange={handleChange} />
      </label>
      <label>
        Discount Rate (%)
        <input
          name="discount_rate"
          type="number"
          value={form.discount_rate}
          onChange={handleChange}
        />
        {errors.discount_rate && (
          <span style={{ color: 'red' }}>{errors.discount_rate}</span>
        )}
      </label>
      <table border={1} cellPadding={4} cellSpacing={0} style={{ width: '100%' }}>
        <thead>
          <tr>
            <th>Product</th>
            <th>Description</th>
            <th>Qty</th>
            <th>Unit Price</th>
            <th>Line Disc %</th>
            <th>Tax %</th>
            <th>Subtotal</th>
            <th>Tax</th>
            <th>Total</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {form.items.map((it, idx) => {
            const { lineSubtotal, lineTax, lineTotal } = calcLine(it)
            return (
              <tr key={idx}>
                <td>
                  <select
                    name="product_id"
                    value={it.product_id}
                    onChange={(e) => handleItemChange(idx, e)}
                  >
                    <option value="">Select...</option>
                    {productsQuery.data?.items.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                </td>
                <td>
                  <input
                    name="description"
                    value={it.description || ''}
                    onChange={(e) => handleItemChange(idx, e)}
                  />
                </td>
                <td>
                  <input
                    name="quantity"
                    type="number"
                    value={it.quantity}
                    onChange={(e) => handleItemChange(idx, e)}
                  />
                </td>
                <td>
                  <input
                    name="unit_price"
                    type="number"
                    value={it.unit_price}
                    onChange={(e) => handleItemChange(idx, e)}
                  />
                </td>
                <td>
                  <input
                    name="line_discount_rate"
                    type="number"
                    value={it.line_discount_rate}
                    onChange={(e) => handleItemChange(idx, e)}
                  />
                </td>
                <td>
                  <input
                    name="tax_rate"
                    type="number"
                    value={it.tax_rate}
                    onChange={(e) => handleItemChange(idx, e)}
                  />
                </td>
                <td>{lineSubtotal.toFixed(2)}</td>
                <td>{lineTax.toFixed(2)}</td>
                <td>{lineTotal.toFixed(2)}</td>
                <td>
                  <button type="button" onClick={() => removeItem(idx)}>
                    Remove
                  </button>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
      <button type="button" onClick={addItem} style={{ width: 'fit-content' }}>
        Add line
      </button>
      <div style={{ alignSelf: 'flex-end', marginTop: '1rem' }}>
        <div>Subtotal: {totals.subtotal.toFixed(2)}</div>
        <div>Tax Total: {totals.tax_total.toFixed(2)}</div>
        <div>Grand Total: {grand.toFixed(2)}</div>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button type="submit">{mode === 'create' ? 'Create' : 'Update'}</button>
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  )
}

export default QuoteForm

