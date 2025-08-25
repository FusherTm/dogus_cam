import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from './api'
import { Partner, PartnerCreate, PartnerUpdate } from '../types/partner'

interface ListParams {
  search: string
  type: string
  page: number
  pageSize: number
}

export const listPartners = ({ search, type, page, pageSize }: ListParams) =>
  useQuery({
    queryKey: ['partners', { search, type, page, pageSize }],
    queryFn: async () => {
      const res = await api.get('/partners', {
        params: { search, type, page, page_size: pageSize },
      })
      return res.data as {
        items: Partner[]
        total: number
        page: number
        page_size: number
      }
    },
  })

export const getPartner = (id: string) =>
  useQuery({
    queryKey: ['partners', id],
    queryFn: async () => {
      const res = await api.get(`/partners/${id}`)
      return res.data as Partner
    },
    enabled: !!id,
  })

export const createPartner = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: PartnerCreate) =>
      api.post('/partners', payload).then((res) => res.data as Partner),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['partners'] })
    },
  })
}

export const updatePartner = (id: string) => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: PartnerUpdate) =>
      api.put(`/partners/${id}`, payload).then((res) => res.data as Partner),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['partners'] })
      queryClient.invalidateQueries({ queryKey: ['partners', id] })
    },
  })
}

export const deletePartner = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.delete(`/partners/${id}`).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['partners'] })
    },
  })
}

