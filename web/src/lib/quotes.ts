import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from './api'
import { Quote, QuoteDetail, QuoteCreate, QuoteUpdate } from '../types/quote'

interface ListParams {
  search: string
  status: string
  partnerId: string
  page: number
  pageSize: number
}

export const listQuotes = ({ search, status, partnerId, page, pageSize }: ListParams) =>
  useQuery({
    queryKey: ['quotes', { search, status, partnerId, page, pageSize }],
    queryFn: async () => {
      const res = await api.get('/sales/quotes', {
        params: { search, status, partner_id: partnerId, page, page_size: pageSize },
      })
      return res.data as {
        items: Quote[]
        total: number
        page: number
        page_size: number
      }
    },
  })

export const getQuote = (id: string) =>
  useQuery({
    queryKey: ['quotes', id],
    queryFn: async () => {
      const res = await api.get(`/sales/quotes/${id}`)
      return res.data as QuoteDetail
    },
    enabled: !!id,
  })

export const createQuote = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: QuoteCreate) =>
      api.post('/sales/quotes', payload).then((res) => res.data as QuoteDetail),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] })
    },
  })
}

export const updateQuote = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: QuoteUpdate }) =>
      api.put(`/sales/quotes/${id}`, payload).then((res) => res.data as QuoteDetail),
    onSuccess: (_data, vars) => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] })
      queryClient.invalidateQueries({ queryKey: ['quotes', vars.id] })
    },
  })
}

export const setQuoteStatus = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      api.post(`/sales/quotes/${id}/status`, { status }).then((res) => res.data as QuoteDetail),
    onSuccess: (_data, vars) => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] })
      queryClient.invalidateQueries({ queryKey: ['quotes', vars.id] })
    },
  })
}

export const convertQuoteToOrder = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) =>
      api.post(`/sales/quotes/${id}/to-order`).then((res) => res.data as any),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] })
    },
  })
}

