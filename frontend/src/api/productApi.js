import client from './client'

export const getProducts = (limit = 50) =>
  client.get(`/products?limit=${limit}`).then((r) => r.data)

export const getProduct = (id) =>
  client.get(`/products/${id}`).then((r) => r.data)

export const searchProducts = (params) =>
  client.post('/products/search', params).then((r) => r.data)
