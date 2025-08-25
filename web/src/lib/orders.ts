import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from './api'
import { Order, OrderDetail, OrderCreate, OrderUpdate } from '../types/order'

interface ListParams {
  search: string
  status: string
  partnerId: string
  page: number
  pageSize: number
}

export const listOrders = ({ search, status, partnerId, page, pageSize }: ListParams) =>
  useQuery({
    queryKey: ['orders', { search, status, partnerId, page, pageSize }],
    queryFn: async () => {
      const res = await api.get('/sales/orders', {
        params: { search, status, partner_id: partnerId, page, page_size: pageSize },
      })
      return res.data as {
        items: Order[]
        total: number
        page: number
        page_size: number
      }
    },
  })

export const getOrder = (id: string) =>
  useQuery({
    queryKey: ['orders', id],
    queryFn: async () => {
      const res = await api.get(`/sales/orders/${id}`)
      return res.data as OrderDetail
    },
    enabled: !!id,
  })

export const createOrder = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: OrderCreate) =>
      api.post('/sales/orders', payload).then((res) => res.data as OrderDetail),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] })
    },
  })
}

export const updateOrder = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: OrderUpdate }) =>
      api.put(`/sales/orders/${id}`, payload).then((res) => res.data as OrderDetail),
    onSuccess: (_data, vars) => {
      queryClient.invalidateQueries({ queryKey: ['orders'] })
      queryClient.invalidateQueries({ queryKey: ['orders', vars.id] })
    },
  })
}

export const setOrderStatus = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      api.post(`/sales/orders/${id}/status`, { status }).then((res) => res.data as OrderDetail),
    onSuccess: (_data, vars) => {
      queryClient.invalidateQueries({ queryKey: ['orders'] })
      queryClient.invalidateQueries({ queryKey: ['orders', vars.id] })
    },
  })
}

