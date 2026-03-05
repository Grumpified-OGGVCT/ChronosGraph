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

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  return (
    <div className="modal-overlay" onClick={onClose} aria-hidden="true">
      <div className="modal video-modal" onClick={e => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="video-modal-title">
        <div className="modal-header">
          <h3 id="video-modal-title"><span aria-hidden="true">🎬</span> Video: {videoId}</h3>
          <button className="icon-btn" onClick={onClose} aria-label="Close video">
             <span aria-hidden="true">✕</span>
          </button>
        </div>
        <video ref={videoRef}
          src={`/api/video/${videoId}`}
          controls
          preload="auto"
          aria-label={`Video player for ${videoId}`}
        />
      </div>
    </div>
  )
}
