import React, { useState, useEffect, useCallback, useRef } from 'react'
import './App.css'
import Header from './components/Header/Header'
import GraphScene from './components/Scene/GraphScene'
import FilterPanel from './components/Filters/FilterPanel'
import Toast from './components/Notifications/Toast'
import ErrorLog from './components/Notifications/ErrorLog'
import VideoModal from './components/VideoModal/VideoModal'
import useWebSocket from './hooks/useWebSocket'
import useGraph from './hooks/useGraph'
import { getFilterMetadata } from './services/api'

function App() {
  const { status: wsStatus, on } = useWebSocket()
  const { graphData, loading, fetchGraph, addNode, addEdge } = useGraph()
  const [systemStatus, setSystemStatus] = useState('idle')
  const [progress, setProgress] = useState(null)
  const [toasts, setToasts] = useState([])
  const [showErrorLog, setShowErrorLog] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState({ types: [], confidence: 0, dateRange: null })
  const [filterMeta, setFilterMeta] = useState({ entity_types: [], date_range: {} })
  const [focusNodeIds, setFocusNodeIds] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const [videoModal, setVideoModal] = useState(null)
  const toastId = useRef(0)

  const addToast = useCallback((level, message) => {
    const id = ++toastId.current
    setToasts(prev => [...prev, { id, level, message }])
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 5000)
  }, [])

  useEffect(() => {
    on('status', (d) => setSystemStatus(d.state))
    on('progress', (d) => setProgress(d))
    on('toast', (d) => addToast(d.level, d.message))
    on('new_node', (d) => addNode(d.node))
    on('new_edge', (d) => addEdge(d.edge))
    on('job_complete', () => { fetchGraph(); setProgress(null) })
    on('queue_update', () => {})
  }, [on, addToast, addNode, addEdge, fetchGraph])

  useEffect(() => {
    getFilterMetadata().then(r => setFilterMeta(r.data)).catch(() => {})
  }, [])

  const handleSearch = useCallback((results) => {
    if (results && results.length > 0) {
      setFocusNodeIds(new Set(results.map(r => r.node_id)))
    } else {
      setFocusNodeIds(null)
    }
  }, [])

  const handleNodeClick = useCallback((node) => {
    setSelectedNode(node)
  }, [])

  const handleVideoClick = useCallback((videoId, timestamp) => {
    setVideoModal({ videoId, timestamp })
  }, [])

  const filteredData = React.useMemo(() => {
    let nodes = graphData.nodes
    let edges = graphData.edges
    if (filters.types.length > 0) {
      const typeSet = new Set(filters.types)
      nodes = nodes.filter(n => typeSet.has(n.type))
    }
    if (filters.confidence > 0) {
      nodes = nodes.filter(n => n.confidence >= filters.confidence)
    }
    const nodeIds = new Set(nodes.map(n => n.id))
    edges = edges.filter(e => nodeIds.has(e.source) && nodeIds.has(e.target))
    return { nodes, edges }
  }, [graphData, filters])

  return (
    <div className="app">
      <Header
        systemStatus={systemStatus}
        wsStatus={wsStatus}
        progress={progress}
        onSearch={handleSearch}
        onToggleErrors={() => setShowErrorLog(!showErrorLog)}
        onToggleFilters={() => setShowFilters(!showFilters)}
      />
      <main className="app-main">
        <GraphScene
          data={filteredData}
          loading={loading}
          focusNodeIds={focusNodeIds}
          selectedNode={selectedNode}
          onNodeClick={handleNodeClick}
          onVideoClick={handleVideoClick}
        />
        {showFilters && (
          <FilterPanel
            metadata={filterMeta}
            filters={filters}
            onChange={setFilters}
            onClose={() => setShowFilters(false)}
          />
        )}
      </main>
      <div className="toast-container">
        {toasts.map(t => <Toast key={t.id} {...t} onDismiss={() =>
          setToasts(prev => prev.filter(x => x.id !== t.id))} />)}
      </div>
      {showErrorLog && <ErrorLog onClose={() => setShowErrorLog(false)} />}
      {videoModal && <VideoModal {...videoModal} onClose={() => setVideoModal(null)} />}
    </div>
  )
}

export default App
