import axios from 'axios'

const API_BASE = '/api'

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const api = {
  // System Health
  getHealth: async () => {
    const res = await axios.get('/health')
    return res.data
  },

  // Papers & Library
  getPapers: async () => {
    const res = await client.get('/papers')
    return res.data
  },
  getPaper: async (id) => {
    const res = await client.get(`/papers/${id}`)
    return res.data
  },
  getPaperElements: async (id, elementType = null) => {
    const params = elementType ? { element_type: elementType } : {}
    const res = await client.get(`/papers/${id}/elements`, { params })
    return res.data
  },
  deletePaper: async (id) => {
    const res = await client.delete(`/papers/${id}`)
    return res.data
  },
  uploadPaper: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await client.post('/ingest/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return res.data
  },

  // Research Assistant Chat
  askChat: async (payload) => {
    const res = await client.post('/chat', payload)
    return res.data
  },

  // Cross-Paper Comparison
  comparePapers: async (payload) => {
    const res = await client.post('/compare', payload)
    return res.data
  },
  listComparisons: async () => {
    const res = await client.get('/compare/list')
    return res.data
  },
  getComparisonCsvUrl: (id) => `/api/compare/${id}/csv`,

  // Research Gap Discovery
  analyzeGaps: async (paperIds) => {
    const res = await client.post('/gaps/analyze', { paper_ids: paperIds })
    return res.data
  },
  listGaps: async () => {
    const res = await client.get('/gaps/list')
    return res.data
  },

  // Knowledge Graph
  getKnowledgeGraph: async (paperIds = null) => {
    const params = paperIds ? { paper_ids: paperIds.join(',') } : {}
    const res = await client.get('/graph', { params })
    return res.data
  },

  // Evaluation & Benchmark
  runBenchmark: async (payload) => {
    const res = await client.post('/eval/run', payload)
    return res.data
  },
  getBenchmarkSummary: async () => {
    const res = await client.get('/eval/summary')
    return res.data
  },
  getBenchmarkHistory: async () => {
    const res = await client.get('/eval/history')
    return res.data
  },
}

