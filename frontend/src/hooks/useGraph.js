import { useState, useEffect, useCallback } from 'react'
import { getGraph } from '../services/api'

export default function useGraph() {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] })
  const [loading, setLoading] = useState(true)

  const fetchGraph = useCallback(async () => {
    try {
      setLoading(true)
      const { data } = await getGraph()
      setGraphData(data)
    } catch (err) {
      console.error('Failed to fetch graph:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchGraph() }, [fetchGraph])

  const addNode = useCallback((node) => {
    setGraphData(prev => ({ ...prev, nodes: [...prev.nodes, node] }))
  }, [])

  const addEdge = useCallback((edge) => {
    setGraphData(prev => ({ ...prev, edges: [...prev.edges, edge] }))
  }, [])

  return { graphData, loading, fetchGraph, addNode, addEdge }
}
