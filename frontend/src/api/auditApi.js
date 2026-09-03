import client from './client'

export const getSessionAudit = (sessionId) =>
  client.get(`/audit/${sessionId}`).then((r) => r.data)

export const getAllAudits = (limit = 100) =>
  client.get(`/audit?limit=${limit}`).then((r) => r.data)

export const getOrderAudit = (orderId) =>
  client.get(`/audit/order/${orderId}`).then((r) => r.data)
