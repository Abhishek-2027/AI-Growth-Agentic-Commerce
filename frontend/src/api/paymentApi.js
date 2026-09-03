import client from './client'

export const createPaymentOrder = (proposalId, sessionId) =>
  client.post('/payments/create-order', { proposal_id: proposalId, session_id: sessionId }).then((r) => r.data)

export const verifyPayment = (data) =>
  client.post('/payments/verify', data).then((r) => r.data)

export const getPaymentStatus = (orderId) =>
  client.get(`/payments/${orderId}/status`).then((r) => r.data)

export const cancelOrder = (orderId) =>
  client.post(`/payments/${orderId}/cancel`).then((r) => r.data)
