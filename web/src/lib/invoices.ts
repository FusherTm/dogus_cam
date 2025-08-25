import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from './api'
import { Invoice, InvoiceDetail, InvoiceCreate, InvoiceUpdate } from '../types/invoice'

interface ListParams {
  search: string
  status: string
  partnerId: string
  page: number
  pageSize: number
}

export const listInvoices = ({ search, status, partnerId, page, pageSize }: ListParams) =>
  useQuery({
    queryKey: ['invoices', { search, status, partnerId, page, pageSize }],
    queryFn: async () => {
      const res = await api.get('/sales/invoices', {
        params: { search, status, partner_id: partnerId, page, page_size: pageSize },
      })
      return res.data as {
        items: Invoice[]
        total: number
        page: number
        page_size: number
      }
    },
  })

export const getInvoice = (id: string) =>
  useQuery({
    queryKey: ['invoices', id],
    queryFn: async () => {
      const res = await api.get(`/sales/invoices/${id}`)
      return res.data as InvoiceDetail
    },
    enabled: !!id,
  })

export const createInvoice = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: InvoiceCreate) =>
      api.post('/sales/invoices', payload).then((res) => res.data as InvoiceDetail),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
    },
  })
}

export const updateInvoice = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: InvoiceUpdate }) =>
      api.put(`/sales/invoices/${id}`, payload).then((res) => res.data as InvoiceDetail),
    onSuccess: (_data, vars) => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
      queryClient.invalidateQueries({ queryKey: ['invoices', vars.id] })
    },
  })
}

export const setInvoiceStatus = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      api.post(`/sales/invoices/${id}/status`, { status }).then((res) => res.data as InvoiceDetail),
    onSuccess: (_data, vars) => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
      queryClient.invalidateQueries({ queryKey: ['invoices', vars.id] })
    },
  })
}

export const getPartnerBalance = (id: string) =>
  useQuery({
    queryKey: ['partner-balance', id],
    queryFn: async () => {
      const res = await api.get(`/finance/ar/balances/${id}`)
      return res.data as { invoice_no: string; issued_total: number; allocated: number; remaining: number }[]
    },
    enabled: !!id,
  })

