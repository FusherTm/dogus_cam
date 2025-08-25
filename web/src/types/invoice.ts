import { z } from 'zod'

export const invoiceItemInSchema = z.object({
  product_id: z.string(),
  description: z.string().optional(),
  quantity: z.number().gt(0),
  unit_price: z.number().min(0),
  line_discount_rate: z.number().min(0).max(100).optional(),
  tax_rate: z.number().min(0).max(100).optional(),
})

export type InvoiceItemIn = z.infer<typeof invoiceItemInSchema>

export const invoiceSchema = z.object({
  id: z.string(),
  number: z.string(),
  partner_id: z.string(),
  order_id: z.string().nullable().optional(),
  currency: z.string(),
  status: z.enum(['DRAFT', 'ISSUED', 'PAID', 'CANCELLED']),
  issue_date: z.string(),
  notes: z.string().optional(),
  discount_rate: z.number().min(0).max(100),
  subtotal: z.number(),
  tax_total: z.number(),
  grand_total: z.number(),
  created_at_utc: z.string(),
})

export type Invoice = z.infer<typeof invoiceSchema>

export const invoiceDetailSchema = invoiceSchema.extend({
  items: z
    .array(
      invoiceItemInSchema.extend({
        line_subtotal: z.number(),
        line_tax: z.number(),
        line_total: z.number(),
      })
    )
    .min(1),
})

export type InvoiceDetail = z.infer<typeof invoiceDetailSchema>

export const invoiceCreateSchema = z.object({
  partner_id: z.string(),
  order_id: z.string().nullable().optional(),
  currency: z.string(),
  issue_date: z.string(),
  notes: z.string().optional(),
  discount_rate: z.number().min(0).max(100).default(0),
  items: z.array(invoiceItemInSchema).min(1),
})

export type InvoiceCreate = z.infer<typeof invoiceCreateSchema>

export const invoiceUpdateSchema = invoiceCreateSchema
export type InvoiceUpdate = z.infer<typeof invoiceUpdateSchema>

