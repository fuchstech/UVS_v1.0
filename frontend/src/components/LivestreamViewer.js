import React, { useState, useEffect, useRef } from 'react';
import './LivestreamViewer.css';
import axios from 'axios';

const LivestreamViewer = ({ onClose, cameraId = 0 }) => {
  const [videoSource, setVideoSource] = useState('camera');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const streamRef = useRef(null);
  const [streamUrl, setStreamUrl] = useState('');
  const [streamStarted, setStreamStarted] = useState(false);

  useEffect(() => {
    // Component mount olduğunda
    if (videoSource === 'camera' && !streamStarted) {
      // Kamera kaynağı seçili ve stream başlatılmamışsa
      startStream();
    }

    // Component unmount olduğunda
    return () => {
      stopStream();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cameraId, videoSource]);

  const startStream = () => {
    setError(null);
    let url;
    
    if (videoSource === 'camera') {
      url = `http://localhost:8000/livestream/?source_type=camera&source_id=${cameraId}`;
      setStreamUrl(url);
    } else if (videoSource === 'video') {
      // Video modu seçildiğinde, eğer stream URL'si yoksa video yüklemeyi bekle
      if (!streamUrl) {
        setError('Lütfen önce video dosyasını yükleyin.');
        setIsStreaming(false);
        return;
      }
      // streamUrl zaten daha önce ayarlandı
      url = streamUrl;
    } else {
      setError('Lütfen bir video dosyası seçin veya kamera kaynağına geçin.');
      return;
    }
    
    setStreamUrl(url);
    setStreamStarted(true);
    setIsStreaming(true);
    
    console.log(`Stream başlatılıyor: ${url}`);
    
    // Akış bağlantısı hata durumunu kontrol et
    if (streamRef.current) {
      streamRef.current.onerror = () => {
        console.error('Stream bağlantı hatası');
        setError('Video akışına bağlanılamadı. Kaynak erişimi kontrol edin.');
        setIsStreaming(false);
        setStreamStarted(false);
      };
    }
  };

  const stopStream = async () => {
    if (isStreaming) {
      setIsStreaming(false);
      setStreamStarted(false);
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

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type.includes('video/')) {
        setSelectedFile(file);
        setError(null);
      } else {
        setSelectedFile(null);
        setError('Lütfen geçerli bir video dosyası seçin.');
      }
    }
  };
  
  const handleVideoUpload = async () => {
    if (!selectedFile) {
      setError('Lütfen bir video dosyası seçin.');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setError(null);

    const formData = new FormData();
    formData.append('video', selectedFile);
    formData.append('stream_mode', 'true');

    try {
      // İlerleme simülasyonu
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          const newProgress = prev + 5;
          if (newProgress >= 95) {
            clearInterval(progressInterval);
            return 95;
          }
          return newProgress;
        });
      }, 300);

      console.log('Video yükleme isteği başladı (stream modu için)');
      console.log('Video boyutu:', (selectedFile.size / (1024 * 1024)).toFixed(2), 'MB');
      
      try {
        // Video dosyasını stream modu için yükle
        const response = await axios.post('http://localhost:8000/upload-stream-video/', formData);
        
        console.log('Video yükleme yanıtı:', response);
        
        clearInterval(progressInterval);
        setUploadProgress(100);
        setIsUploading(false);
        
        // Video ID'sini al ve URL'yi ayarla
        if (response.data && response.data.video_id) {
        const videoId = response.data.video_id;
        // videoId doğrudan dosya adı olarak kullanılıyor
        console.log('Stream için video ID alındı:', videoId);
        const newStreamUrl = `http://localhost:8000/livestream/?source_type=video&source_id=${videoId}`;
        console.log('Stream URL ayarlandı:', newStreamUrl);
        setStreamUrl(newStreamUrl);
        
          // Önemli: Biraz bekle ve sonra stream'i başlat
            setTimeout(() => {
              startStream();
            }, 1000); // 1 saniye bekle
          } else {
          setError('Video yüklendi ancak ID alınamadı.');
        }
      } catch (error) {
        console.error('Video yükleme hatası:', error);
        clearInterval(progressInterval);
        setIsUploading(false);
        
        const errorMessage = error.response?.data?.detail || 
                           error.response?.data?.error ||
                           error.message || 
                           'Video yüklenirken bir hata oluştu.';
                           
        setError(`Hata: ${errorMessage}`);
      }
    } catch (e) {
      console.error('Genel hata:', e);
      setIsUploading(false);
      setError(`Beklenmeyen bir hata oluştu: ${e.message}`);
    }
  };

  return (
    <div className="livestream-container">
      <div className="livestream-header">
        <h3>Gerçek Zamanlı Baret Tespiti</h3>
        <div className="source-selector">
          <label className="switch">
            <input
              type="checkbox"
              checked={videoSource === 'video'}
              onChange={() => {
                if (isStreaming) stopStream();
                // Geçiş yapılırken stream'i sıfırla
                setStreamUrl('');
                setVideoSource(videoSource === 'camera' ? 'video' : 'camera');
              }}
            />
            <span className="slider round"></span>
          </label>
          <span className="source-label">{videoSource === 'camera' ? 'Kamera' : 'Video'}</span>
        </div>
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
        {videoSource === 'video' && !isStreaming ? (
          <div className="video-upload-section">
            <div className="form-group">
              <label htmlFor="video-file">Video Dosyası:</label>
              <input
                type="file"
                id="video-file"
                accept="video/*"
                onChange={handleFileChange}
                disabled={isUploading}
              />
              {selectedFile && (
                <div className="file-info">
                  <span>Seçilen Dosya: {selectedFile.name}</span>
                  <span>Boyut: {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
                </div>
              )}
            </div>
            
            {error && <div className="error-message">{error}</div>}
            
            {isUploading ? (
              <div className="upload-progress">
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
                </div>
                <span>{uploadProgress}% Yükleniyor...</span>
              </div>
            ) : (
              <button 
                className="upload-button"
                onClick={handleVideoUpload}
                disabled={!selectedFile || isUploading}
              >
                Video Yükle ve İşlemeye Başla
              </button>
            )}
          </div>
        ) : isStreaming ? (
          <>
            <img 
              ref={streamRef}
              className="stream-image" 
              src={streamUrl}
              alt={videoSource === 'camera' ? "Canlı Kamera Akışı" : "Video Akışı"}
              onError={(e) => {
                console.error("Görüntü yükleme hatası:", e);
                setError("Görüntü akışı yüklenemedi. Sunucu bağlantısını kontrol edin.");
              }} 
            />
            <div className="debug-info">
              <p>Stream URL: {streamUrl}</p>
              <p>Stream durumu: {isStreaming ? 'Aktif' : 'Durduruldu'}</p>
              <button onClick={() => {
                console.log("Stream URL:", streamUrl);
                console.log("Stream durumu:", isStreaming ? 'Aktif' : 'Durduruldu');
              }}>Hata Ayıklama Bilgisi</button>
            </div>
          </>
        ) : (
          <div className="no-stream">
            {error ? (
              <div className="error-message">{error}</div>
            ) : (
              <div className="instructions">
                <p>{videoSource === 'camera' ? 'Kamera' : 'Video'} akışı şu anda kapalı.</p>
                <p>"Akışı Başlat" butonuna tıklayarak görüntü işlemeyi başlatabilirsiniz.</p>
                {videoSource === 'camera' && <p><strong>Not:</strong> Bu özellik, kameraya erişim gerektirir.</p>}
              </div>
            )}
          </div>
        )}
      </div>
      
      <div className="livestream-footer">
        <div className="stream-info">
          <p>Baret tespiti için YOLO modeli kullanılıyor - ({videoSource === 'camera' ? `Kamera ID: ${cameraId}` : 'Video Kaynağı'})</p>
        </div>
      </div>
    </div>
  );
};

export default LivestreamViewer;