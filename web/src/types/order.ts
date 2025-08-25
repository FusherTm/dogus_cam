import { z } from 'zod'

export const orderItemInSchema = z.object({
  product_id: z.string(),
  description: z.string().optional(),
  quantity: z.number().gt(0),
  unit_price: z.number().min(0),
  line_discount_rate: z.number().min(0).max(100).optional(),
  tax_rate: z.number().min(0).max(100).optional(),
})

export type OrderItemIn = z.infer<typeof orderItemInSchema>

export const orderSchema = z.object({
  id: z.string(),
  number: z.string(),
  partner_id: z.string(),
  currency: z.string(),
  status: z.enum(['NEW', 'CONFIRMED', 'FULFILLED', 'CANCELLED']),
  order_date: z.string(),
  notes: z.string().optional(),
  discount_rate: z.number().min(0).max(100),
  subtotal: z.number(),
  tax_total: z.number(),
  grand_total: z.number(),
  created_at_utc: z.string(),
})

export type Order = z.infer<typeof orderSchema>

export const orderDetailSchema = orderSchema.extend({
  items: z
    .array(
      orderItemInSchema.extend({
        line_subtotal: z.number(),
        line_tax: z.number(),
        line_total: z.number(),
      })
    )
    .min(1),
})

export type OrderDetail = z.infer<typeof orderDetailSchema>

export const orderCreateSchema = z.object({
  partner_id: z.string(),
  currency: z.string(),
  order_date: z.string(),
  notes: z.string().optional(),
  discount_rate: z.number().min(0).max(100).default(0),
  items: z.array(orderItemInSchema).min(1),
})

export type OrderCreate = z.infer<typeof orderCreateSchema>

export const orderUpdateSchema = orderCreateSchema
export type OrderUpdate = z.infer<typeof orderUpdateSchema>

