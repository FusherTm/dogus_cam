import { z } from 'zod'

export const dashboardSummarySchema = z.object({
  salesToday: z.number(),
  salesThisMonth: z.number(),
  receivablesTotal: z.number(),
  receivablesAging: z.array(
    z.object({
      period: z.string(),
      amount: z.number(),
    })
  ),
  lowStock: z.array(
    z.object({
      sku: z.string(),
      name: z.string(),
      total: z.number(),
      restock_level: z.number(),
    })
  ),
  topCustomers: z.array(
    z.object({
      name: z.string(),
      total: z.number(),
    })
  ),
})

export type DashboardSummary = z.infer<typeof dashboardSummarySchema>
