import { z } from 'zod'

export const partnerSchema = z.object({
  id: z.string(),
  name: z.string().min(2).max(120),
  type: z.enum(['customer', 'supplier', 'both']),
  email: z.string().email().optional(),
  phone: z.string().min(5).optional(),
  tax_number: z.string().min(5).max(20).optional(),
  billing_address: z.string().optional(),
  shipping_address: z.string().optional(),
  is_active: z.boolean(),
  created_at_utc: z.string(),
})

export type Partner = z.infer<typeof partnerSchema>

export const partnerCreateSchema = partnerSchema
  .omit({ id: true, created_at_utc: true })
  .extend({
    is_active: z.boolean().optional(),
  })

export type PartnerCreate = z.infer<typeof partnerCreateSchema>

export const partnerUpdateSchema = partnerCreateSchema.partial()
export type PartnerUpdate = z.infer<typeof partnerUpdateSchema>

