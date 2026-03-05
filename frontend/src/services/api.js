import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

export const ingestUrl = (url) => api.post('/ingest', { url })
export const searchEntities = (q, limit = 20) => api.get('/search', { params: { q, limit } })
export const getGraph = () => api.get('/graph')
export const getNodeDetail = (id) => api.get(`/graph/node/${id}`)
export const getErrors = () => api.get('/errors')
export const retryError = (id) => api.post(`/errors/${id}/retry`)
export const getFilterMetadata = () => api.get('/filters/metadata')

export default api
