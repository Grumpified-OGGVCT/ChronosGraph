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

  // Advanced Cluster View (>5,000 nodes -> SuperNodes)
  // Preserves all existing nodes, injects gravitational SuperNodes
  const { processedNodes, processedEdges } = useMemo(() => {
    let nodes = [...data.nodes];
    let edges = [...data.edges];

    if (data.nodes.length > 5000) {
      const typeGroups = new Map();

      // Group existing nodes by type
      data.nodes.forEach(n => {
        if (!typeGroups.has(n.type)) typeGroups.set(n.type, []);
        typeGroups.get(n.type).push(n);
      });

      // Inject SuperNodes and tether existing nodes to them
      typeGroups.forEach((nodesOfType, type) => {
        const superNodeId = `supernode-${type}`;

        // Only create a SuperNode if the cluster is significant
        if (nodesOfType.length > 5) {
          nodes.push({
            id: superNodeId,
            name: `${type} Cluster`,
            type: type,
            mention_count: nodesOfType.length * 2, // Make it visibly larger
            isSuperNode: true,
            data_quality: 'complete'
          });

          // Tether nodes to their SuperNode
          nodesOfType.forEach(n => {
            edges.push({
              source: n.id,
              target: superNodeId,
              type: 'TETHER',
              isTether: true
            });
          });
        }
      });
    }

    return { processedNodes: nodes, processedEdges: edges };
  }, [data.nodes, data.edges]);

  // Build or Update simulation reactively
  useEffect(() => {
    if (!processedNodes.length) return

    // Map new props to mutable physics nodes, preserving existing position/velocity
    const nodes = processedNodes.map(n => {
      // Find existing node in running simulation if it exists
      const existingSimNode = simRef.current?.nodes?.find(old => old.id === n.id)
      const existingPos = positionsRef.current.get(n.id)

      return {
        ...n,
        x: existingSimNode?.x || existingPos?.x || (Math.random() - 0.5) * 100,
        y: existingSimNode?.y || existingPos?.y || (Math.random() - 0.5) * 100,
        z: existingSimNode?.z || existingPos?.z || (Math.random() - 0.5) * 100,
        vx: existingSimNode?.vx || 0,
        vy: existingSimNode?.vy || 0,
        vz: existingSimNode?.vz || 0,
        _birth: existingSimNode?._birth || existingPos?._birth || Date.now()
      }
    })

    const links = processedEdges.map(e => ({ source: e.source, target: e.target, isTether: e.isTether }))

    if (!simRef.current) {
      // Initialize new simulation
      const sim = forceSimulation(nodes, 3)
        .force('charge', forceManyBody().strength(-120))
        .force('link', forceLink(links).id(d => d.id).distance(l => l.isTether ? 15 : 40))
        .force('center', forceCenter())

      sim.alpha(1).restart()
      simRef.current = { sim, nodes, links }
    } else {
      // Reactively update existing simulation
      simRef.current.sim.nodes(nodes)
      simRef.current.sim.force('link').links(links)

      // Give a small energy bump to allow new nodes to settle without exploding layout
      simRef.current.sim.alpha(0.1).restart()

      simRef.current.nodes = nodes
      simRef.current.links = links
    }

    return () => {
      // We don't stop the simulation on unmount/re-render to allow it to run continuously
      // Only stop it if the component fully unmounts, handled in a separate hook if needed.
    }
  }, [processedNodes, processedEdges])

  // Cleanup simulation on full unmount
  useEffect(() => {
    return () => {
      if (simRef.current?.sim) simRef.current.sim.stop()
    }
  }, [])

  // Force animation to continue even if sim cools down for growing nodes
  useFrame(() => {
    if (!simRef.current || !meshRef.current) return
    const { nodes } = simRef.current
    const dummy = new THREE.Object3D()
    const color = new THREE.Color()

    nodes.forEach((node, i) => {
      positionsRef.current.set(node.id, { x: node.x, y: node.y, z: node.z, _birth: node._birth })

      // Self-growing animation (fade-in/scale-up)
      if (!node._birth) node._birth = Date.now()
      const age = Date.now() - node._birth
      const animScale = Math.min(1, age / 800) // 800ms growth animation

      const scale = 0.5 + Math.log2(Math.max(1, node.mention_count || 1)) * 0.3
      const isFocused = !focusNodeIds || focusNodeIds.has(node.id)
      const isHovered = hoveredId === node.id
      const targetScale = isHovered ? scale * 1.5 : isFocused ? scale : scale * 0.4
      const finalScale = targetScale * animScale

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
        if (s && t && s.x !== undefined && t.x !== undefined) {
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

  const nodeCount = processedNodes.length;
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
            <div className="node-tooltip" role="tooltip">
              <div className="tt-name">{node.name}</div>
              <div className="tt-type" style={{color: TYPE_COLORS[node.type]}}>{node.type}</div>
              {node.data_quality === 'partial' && (
                <div className="tt-warning" style={{color: 'var(--warning)', fontSize: '10px', marginTop: '4px'}}>
                  <span aria-hidden="true">⚠️</span> Partial Data
                </div>
              )}
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
            <div className="holo-card" role="region" aria-label="Node Details">
              <button className="close-card" onClick={() => setSelectedNode(null)} aria-label="Close details">✕</button>
              <h4 id={`holo-title-${selectedNode.id}`}>{selectedNode.name}</h4>
              <div className="entity-type" style={{color: TYPE_COLORS[selectedNode.type]}}>
                {selectedNode.type}
                {selectedNode.data_quality === 'partial' && (
                  <span style={{color: 'var(--warning)', marginLeft: '8px', fontSize: '10px'}} title="Partial data: node context incomplete">
                    <span aria-hidden="true">⚠️</span> Partial Data
                  </span>
                )}
              </div>
              <div className="entity-desc">{selectedNode.description || 'No description available'}</div>
              {selectedNode.video_sources && selectedNode.video_sources.length > 0 && (
                <ul className="evidence-list" aria-label="Video Sources">
                  {selectedNode.video_sources.slice(0, 5).map((vs, i) => (
                    <li
                      key={i}
                      onClick={() => onVideoClick?.(vs.video_id, vs.timestamp)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          onVideoClick?.(vs.video_id, vs.timestamp);
                        }
                      }}
                      tabIndex={0}
                      role="button"
                      aria-label={`Open video ${vs.video_id} at ${vs.timestamp || '0:00'}`}
                    >
                      <span aria-hidden="true">🎬</span> {vs.video_id} @ {vs.timestamp || '0:00'}
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
      <div className="scene-loading" role="status" aria-live="polite">
        <div className="spinner" aria-hidden="true" />
        <span>Loading Knowledge Graph...</span>
      </div>
    )
  }

  return (
    <div className="graph-scene" aria-label="Knowledge Graph Visualization" role="application">
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
      <div className="node-count" aria-live="polite" aria-atomic="true">
        {data.nodes.length} nodes · {data.edges.length} edges
      </div>
    </div>
  )
}
