import React, { useState, useEffect, useRef } from 'react';
import './LivestreamViewer.css';

const LivestreamViewer = ({ onClose, cameraId = 0 }) => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const streamRef = useRef(null);
  const [streamUrl, setStreamUrl] = useState('');

  useEffect(() => {
    // Component mount olduğunda
    startStream();

    // Component unmount olduğunda
    return () => {
      stopStream();
    };
  }, [cameraId]);

  const startStream = () => {
    setError(null);
    const url = `http://localhost:8000/livestream/?camera_id=${cameraId}`;
    setStreamUrl(url);
    setIsStreaming(true);
    
    // Akış bağlantısı hata durumunu kontrol et
    if (streamRef.current) {
      streamRef.current.onerror = () => {
        console.error('Stream bağlantı hatası');
        setError('Video akışına bağlanılamadı. Kamera erişimi kontrol edin.');
        setIsStreaming(false);
      };
    }
  };

  const stopStream = async () => {
    if (isStreaming) {
      setIsStreaming(false);
      try {
        // Stream'i durdurmak için DELETE isteği gönder
        await fetch('http://localhost:8000/livestream/', {
          method: 'DELETE',
        });
        console.log('Stream durduruldu');
      } catch (err) {
        console.error('Stream durdurma hatası:', err);
      }
    }
  };

  return (
    <div className="livestream-container">
      <div className="livestream-header">
        <h3>Canlı Baret Tespiti</h3>
        <div className="controls">
          <button 
            className={`stream-button ${isStreaming ? 'stop' : 'start'}`}
            onClick={isStreaming ? stopStream : startStream}
          >
            {isStreaming ? 'Akışı Durdur' : 'Akışı Başlat'}
          </button>
          {onClose && (
            <button className="close-button" onClick={onClose}>
              Kapat
            </button>
          )}
        </div>
      </div>
      
      <div className="stream-container">
        {isStreaming ? (
          <img 
            ref={streamRef}
            className="stream-image" 
            src={streamUrl}
            alt="Canlı Kamera Akışı" 
          />
        ) : (
          <div className="no-stream">
            {error ? (
              <div className="error-message">{error}</div>
            ) : (
              <div className="instructions">
                <p>Kamera akışı şu anda kapalı.</p>
                <p>"Akışı Başlat" butonuna tıklayarak canlı görüntü alabilirsiniz.</p>
                <p><strong>Not:</strong> Bu özellik, kameraya erişim gerektirir.</p>
              </div>
            )}
          </div>
        )}
      </div>
      
      <div className="livestream-footer">
        <div className="stream-info">
          <p>Baret tespiti için YOLO modeli kullanılıyor - (Kamera ID: {cameraId})</p>
        </div>
      </div>
    </div>
  );
};

export default LivestreamViewer;