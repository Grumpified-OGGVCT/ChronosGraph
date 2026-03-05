import React, { useRef, useMemo, useState, useCallback, useEffect } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'
import { forceSimulation, forceManyBody, forceLink, forceCenter } from 'd3-force-3d'

const TYPE_COLORS = {
  Person: '#00d4ff', Organization: '#ff6b35', Concept: '#a855f7',
  Event: '#22c55e', Location: '#eab308',
}

function ForceGraph({ data, focusNodeIds, onNodeClick, onVideoClick }) {
  const meshRef = useRef()
  const linesRef = useRef()
  const [hoveredId, setHoveredId] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const { camera } = useThree()
  const simRef = useRef(null)
  const positionsRef = useRef(new Map())

  // Build simulation
  useEffect(() => {
    if (!data.nodes.length) return
    const nodes = data.nodes.map(n => ({
      ...n, x: positionsRef.current.get(n.id)?.x || (Math.random() - 0.5) * 100,
      y: positionsRef.current.get(n.id)?.y || (Math.random() - 0.5) * 100,
      z: positionsRef.current.get(n.id)?.z || (Math.random() - 0.5) * 100,
    }))
    const links = data.edges.map(e => ({ source: e.source, target: e.target }))
    const sim = forceSimulation(nodes, 3)
      .force('charge', forceManyBody().strength(-120))
      .force('link', forceLink(links).id(d => d.id).distance(40))
      .force('center', forceCenter())
    sim.alpha(0.3).restart()
    simRef.current = { sim, nodes, links }
    return () => sim.stop()
  }, [data.nodes.length, data.edges.length])

  // Update instanced mesh positions
  useFrame(() => {
    if (!simRef.current || !meshRef.current) return
    const { nodes } = simRef.current
    const dummy = new THREE.Object3D()
    const color = new THREE.Color()

    nodes.forEach((node, i) => {
      positionsRef.current.set(node.id, { x: node.x, y: node.y, z: node.z })
      const scale = 0.5 + Math.log2(Math.max(1, node.mention_count || 1)) * 0.3
      const isFocused = !focusNodeIds || focusNodeIds.has(node.id)
      const isHovered = hoveredId === node.id
      const finalScale = isHovered ? scale * 1.5 : isFocused ? scale : scale * 0.4

      dummy.position.set(node.x || 0, node.y || 0, node.z || 0)
      dummy.scale.setScalar(finalScale)
      dummy.updateMatrix()
      meshRef.current.setMatrixAt(i, dummy.matrix)

      const c = TYPE_COLORS[node.type] || '#888888'
      color.set(c)
      if (!isFocused) color.multiplyScalar(0.3)
      meshRef.current.setColorAt(i, color)
    })
    meshRef.current.instanceMatrix.needsUpdate = true
    if (meshRef.current.instanceColor) meshRef.current.instanceColor.needsUpdate = true

    // Update edges
    if (linesRef.current && simRef.current.links) {
      const positions = []
      simRef.current.links.forEach(link => {
        const s = typeof link.source === 'object' ? link.source : simRef.current.nodes.find(n => n.id === link.source)
        const t = typeof link.target === 'object' ? link.target : simRef.current.nodes.find(n => n.id === link.target)
        if (s && t) {
          positions.push(s.x || 0, s.y || 0, s.z || 0)
          positions.push(t.x || 0, t.y || 0, t.z || 0)
        }
      })
      linesRef.current.geometry.setAttribute('position',
        new THREE.Float32BufferAttribute(positions, 3))
    }
  })

  const handlePointerMove = useCallback((e) => {
    if (e.instanceId !== undefined && simRef.current) {
      const node = simRef.current.nodes[e.instanceId]
      setHoveredId(node?.id || null)
    }
  }, [])

  const handleClick = useCallback((e) => {
    if (e.instanceId !== undefined && simRef.current) {
      const node = simRef.current.nodes[e.instanceId]
      if (node) {
        setSelectedNode(node)
        onNodeClick?.(node)
        // Lerp camera towards node
        const target = new THREE.Vector3(node.x, node.y, node.z + 40)
        camera.position.lerp(target, 0.3)
      }
    }
  }, [camera, onNodeClick])

  const nodeCount = data.nodes.length
  if (nodeCount === 0) return null

  return (
    <>
      <instancedMesh ref={meshRef} args={[null, null, nodeCount]}
        onPointerMove={handlePointerMove}
        onPointerLeave={() => setHoveredId(null)}
        onClick={handleClick}>
        <sphereGeometry args={[1, 16, 12]} />
        <meshStandardMaterial roughness={0.4} metalness={0.6} />
      </instancedMesh>

      <lineSegments ref={linesRef}>
        <bufferGeometry />
        <lineBasicMaterial color="#334455" opacity={0.4} transparent />
      </lineSegments>

      {/* Tooltip on hover */}
      {hoveredId && simRef.current && (() => {
        const node = simRef.current.nodes.find(n => n.id === hoveredId)
        if (!node) return null
        return (
          <Html position={[node.x, node.y + 2, node.z]} center style={{pointerEvents:'none'}}>
            <div className="node-tooltip">
              <div className="tt-name">{node.name}</div>
              <div className="tt-type" style={{color: TYPE_COLORS[node.type]}}>{node.type}</div>
            </div>
          </Html>
        )
      })()}

      {/* HoloCard on selection */}
      {selectedNode && (() => {
        const pos = positionsRef.current.get(selectedNode.id)
        if (!pos) return null
        return (
          <Html position={[pos.x + 3, pos.y, pos.z]} style={{pointerEvents:'auto'}}>
            <div className="holo-card">
              <button className="close-card" onClick={() => setSelectedNode(null)}>✕</button>
              <h4>{selectedNode.name}</h4>
              <div className="entity-type" style={{color: TYPE_COLORS[selectedNode.type]}}>
                {selectedNode.type}
              </div>
              <div className="entity-desc">{selectedNode.description || 'No description available'}</div>
              {selectedNode.video_sources && selectedNode.video_sources.length > 0 && (
                <ul className="evidence-list">
                  {selectedNode.video_sources.slice(0, 5).map((vs, i) => (
                    <li key={i} onClick={() => onVideoClick?.(vs.video_id, vs.timestamp)}>
                      🎬 {vs.video_id} @ {vs.timestamp || '0:00'}
                    </li>
                  ))}
                </ul>
              )}
              <div style={{fontSize:'11px',color:'var(--text-muted)'}}>
                Mentioned {selectedNode.mention_count || 1}x · Confidence: {((selectedNode.confidence || 0) * 100).toFixed(0)}%
              </div>
            </div>
          </Html>
        )
      })()}
    </>
  )
}

export default function GraphScene({ data, loading, focusNodeIds, selectedNode, onNodeClick, onVideoClick }) {
  if (loading) {
    return (
      <div className="scene-loading">
        <div className="spinner" />
        <span>Loading Knowledge Graph...</span>
      </div>
    )
  }

  return (
    <div className="graph-scene">
      <Canvas camera={{ position: [0, 50, 150], fov: 60 }} gl={{ antialias: true, alpha: false }}
        style={{ background: '#0a0a0f' }}>
        <ambientLight intensity={0.4} />
        <pointLight position={[50, 80, 50]} intensity={0.8} />
        <pointLight position={[-50, -50, -50]} intensity={0.3} color="#a855f7" />
        <gridHelper args={[200, 40, '#1a1a2e', '#1a1a2e']} position={[0, -50, 0]} />
        <ForceGraph data={data} focusNodeIds={focusNodeIds}
          onNodeClick={onNodeClick} onVideoClick={onVideoClick} />
        <OrbitControls enableDamping dampingFactor={0.08} minDistance={10} maxDistance={500} />
      </Canvas>
      <div className="node-count">
        {data.nodes.length} nodes · {data.edges.length} edges
      </div>
    </div>
  )
}
