import client from './client'

export const getOrders = () => client.get('/orders').then((r) => r.data)
export const getOrder = (id) => client.get(`/orders/${id}`).then((r) => r.data)

export const getProposal = (id) => client.get(`/purchase/${id}`).then((r) => r.data)
export const approveProposal = (id, sessionId) =>
  client.post(`/purchase/${id}/approve`, { session_id: sessionId }).then((r) => r.data)
export const rejectProposal = (id, sessionId) =>
  client.post(`/purchase/${id}/reject`, { session_id: sessionId }).then((r) => r.data)
