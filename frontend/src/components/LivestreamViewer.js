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
  // Alternatif mod için state
  const [useAltMode, setUseAltMode] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(null);
  const [frameUrl, setFrameUrl] = useState('');

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

  // Alternatif mod için fonksiyon
  const startAlternativeMode = () => {
    // Parametreleri oluştur
    let source_type = videoSource === 'camera' ? 'camera' : 'video';
    let source_id = videoSource === 'camera' ? cameraId : streamUrl.split('source_id=')[1];
    
    // Alternatif mod base URL
    const baseUrl = `/livestream/?alt_mode=true&source_type=${source_type}&source_id=${source_id}`;
    
    // İlk kareyi al
    setFrameUrl(`${baseUrl}&ts=${new Date().getTime()}`);
    
    // Başlatma statüsünü güncelle
    setIsStreaming(true);
    setStreamStarted(true);
    
    // Saniyede 5 kez yeni kareler iste (200ms)
    const interval = setInterval(() => {
      setFrameUrl(`${baseUrl}&ts=${new Date().getTime()}`);
    }, 200);
    
    setRefreshInterval(interval);
    
    console.log('Alternatif streaming modu başlatıldı');
  };
  
  const startStream = () => {
    setError(null);
    
    // Önce mevcut stream'i temizle
    if (isStreaming) {
      stopStream();
    }
    
    // Alternatif modu kullan?    
    if (useAltMode) {
      startAlternativeMode();
      return;
    }
    
    let url;
    
    if (videoSource === 'camera') {
      // Tam URL yerine göreceli URL kullan
      url = `/livestream/?source_type=camera&source_id=${cameraId}`;
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
      
      // Alternatif mod aktifse interval'i temizle
      if (useAltMode && refreshInterval) {
        clearInterval(refreshInterval);
        setRefreshInterval(null);
        setFrameUrl('');
        console.log('Alternatif streaming modu durduruldu');
        return;
      }
      
      try {
        // Stream'i durdurmak için DELETE isteği gönder
        await fetch('/livestream/', {
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
        const response = await axios.post('/upload-stream-video/', formData);
        
        console.log('Video yükleme yanıtı:', response);
        
        clearInterval(progressInterval);
        setUploadProgress(100);
        setIsUploading(false);
        
        // Video ID'sini al ve URL'yi ayarla
        if (response.data && response.data.video_id) {
        const videoId = response.data.video_id;
        // göreceli URL kullan
        const newStreamUrl = `/livestream/?source_type=video&source_id=${videoId}`;
        setStreamUrl(newStreamUrl);
        console.log('Stream URL ayarlandı:', newStreamUrl);
        
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
            {useAltMode ? (
              // Alternatif mod için
              <img 
                className="stream-image" 
                src={frameUrl}
                alt={videoSource === 'camera' ? "Canlı Kamera Kar Akışı" : "Video Kare Akışı"}
                onError={(e) => {
                  console.error("Alternatif mod görüntü hatası:", e);
                  setError("Görüntü yüklenemedi. Yönetici haklarını kontrol edin.");
                }} 
              />
            ) : (
              // Normal MJPEG akış modu için
              <img 
                ref={streamRef}
                className="stream-image" 
                src={streamUrl}
                alt={videoSource === 'camera' ? "Canlı Kamera Akışı" : "Video Akışı"}
                onError={(e) => {
                  console.error("Görüntü yükleme hatası:", e);
                  setError("Görüntü akışı yüklenemedi. Alternatif modu deneyebilirsiniz.");
                  // Eğer normal mod başarısız olursa, alternatif modu öner
                  setUseAltMode(true);
                }} 
              />
            )}
            <div className="debug-info">
              <p>Stream Mod: {useAltMode ? 'Alternatif (kare bazlı)' : 'Normal (MJPEG)'}</p>
              <p>Stream URL: {useAltMode ? frameUrl : streamUrl}</p>
              <p>Stream durumu: {isStreaming ? 'Aktif' : 'Durduruldu'}</p>
              <button 
                className="mode-toggle-button"
                onClick={() => {
                  // Akış modunu değiştir
                  setUseAltMode(!useAltMode);
                  console.log("Akış modu değiştirildi:", !useAltMode ? 'Alternatif' : 'Normal');
                  // Mevcut akışı durdur ve yeni modda yeniden başlat
                  stopStream();
                  setTimeout(() => startStream(), 500);
                }}
              >
                {useAltMode ? 'Normal Moda Geç' : 'Alternatif Moda Geç'}
              </button>
              <button onClick={() => {
                console.log("Stream bilgileri:", {
                  mod: useAltMode ? 'Alternatif' : 'Normal', 
                  url: useAltMode ? frameUrl : streamUrl,
                  durum: isStreaming ? 'Aktif' : 'Durduruldu'
                });
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