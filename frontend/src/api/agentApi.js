import client from './client'

export const sendMessage = (message, sessionId) =>
  client.post('/agent/chat', { message, session_id: sessionId }).then((r) => r.data)

export const getSession = (sessionId) =>
  client.get(`/agent/session/${sessionId}`).then((r) => r.data)
