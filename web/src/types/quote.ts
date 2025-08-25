import { z } from 'zod'

export const quoteItemInSchema = z.object({
  product_id: z.string(),
  description: z.string().optional(),
  quantity: z.number().gt(0),
  unit_price: z.number().min(0),
  line_discount_rate: z.number().min(0).max(100).optional(),
  tax_rate: z.number().min(0).max(100).optional(),
})

export type QuoteItemIn = z.infer<typeof quoteItemInSchema>

export const quoteSchema = z.object({
  id: z.string(),
  number: z.string(),
  partner_id: z.string(),
  currency: z.string(),
  status: z.enum(['DRAFT', 'SENT', 'APPROVED', 'REJECTED', 'EXPIRED']),
  issue_date: z.string(),
  valid_until: z.string().optional(),
  notes: z.string().optional(),
  discount_rate: z.number().min(0).max(100),
  subtotal: z.number(),
  tax_total: z.number(),
  grand_total: z.number(),
  created_at_utc: z.string(),
})

export type Quote = z.infer<typeof quoteSchema>

export const quoteDetailSchema = quoteSchema.extend({
  items: z
    .array(
      quoteItemInSchema.extend({
        line_subtotal: z.number(),
        line_tax: z.number(),
        line_total: z.number(),
      })
    )
    .min(1),
})

export type QuoteDetail = z.infer<typeof quoteDetailSchema>

export const quoteCreateSchema = z.object({
  partner_id: z.string(),
  currency: z.string(),
  issue_date: z.string(),
  valid_until: z.string().optional(),
  notes: z.string().optional(),
  discount_rate: z.number().min(0).max(100).default(0),
  items: z.array(quoteItemInSchema).min(1),
})

export type QuoteCreate = z.infer<typeof quoteCreateSchema>

export const quoteUpdateSchema = quoteCreateSchema
export type QuoteUpdate = z.infer<typeof quoteUpdateSchema>

