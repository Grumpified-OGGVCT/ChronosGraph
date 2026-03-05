import React, { useEffect, useRef } from 'react'

export default function VideoModal({ videoId, timestamp, onClose }) {
  const videoRef = useRef(null)

  useEffect(() => {
    if (videoRef.current && timestamp) {
      const parts = timestamp.split(':')
      let seconds = 0
      if (parts.length === 3) seconds = +parts[0] * 3600 + +parts[1] * 60 + +parts[2]
      else if (parts.length === 2) seconds = +parts[0] * 60 + +parts[1]
      else seconds = +parts[0]
      videoRef.current.currentTime = seconds
      videoRef.current.play().catch(() => {})
    }
  }, [timestamp])

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal video-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>🎬 Video: {videoId}</h3>
          <button className="icon-btn" onClick={onClose}>✕</button>
        </div>
        <video ref={videoRef}
          src={`/api/video/${videoId}`}
          controls
          preload="auto"
        />
      </div>
    </div>
  )
}
