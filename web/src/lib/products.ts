import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from './api'
import { Product, ProductCreate, ProductUpdate } from '../types/product'

interface ListParams {
  search: string
  page: number
  pageSize: number
}

export const listProducts = ({ search, page, pageSize }: ListParams) => {
  const skip = (page - 1) * pageSize
  return useQuery({
    queryKey: ['products', { search, page, pageSize }],
    queryFn: async () => {
      const res = await api.get('/products', {
        params: { search, skip, take: pageSize },
      })
      return res.data as {
        items: Product[]
        total: number
        page: number
        page_size: number
      }
    },
  })
}

export const getProduct = (id: string) =>
  useQuery({
    queryKey: ['products', id],
    queryFn: async () => {
      const res = await api.get(`/products/${id}`)
      return res.data as Product
    },
    enabled: !!id,
  })

export const createProduct = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: ProductCreate) =>
      api.post('/products', payload).then((res) => res.data as Product),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
  })
}

export const updateProduct = (id: string) => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: ProductUpdate) =>
      api.put(`/products/${id}`, payload).then((res) => res.data as Product),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      queryClient.invalidateQueries({ queryKey: ['products', id] })
    },
  })
}

export const deleteProduct = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.delete(`/products/${id}`).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
  })
}

