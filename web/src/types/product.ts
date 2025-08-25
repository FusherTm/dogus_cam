import { z } from 'zod'

export const productSchema = z.object({
  id: z.string(),
  name: z.string().min(2).max(120),
  sku: z.string().regex(/^[A-Za-z0-9_-]{3,40}$/),
  price: z.number().min(0),
  is_active: z.boolean(),
  created_at_utc: z.string(),
  restock_level: z.number().min(0).optional(),
})

export type Product = z.infer<typeof productSchema>

export const productCreateSchema = productSchema
  .omit({ id: true, created_at_utc: true })
  .extend({
    is_active: z.boolean().optional(),
  })

export type ProductCreate = z.infer<typeof productCreateSchema>

export const productUpdateSchema = productCreateSchema.partial()
export type ProductUpdate = z.infer<typeof productUpdateSchema>

