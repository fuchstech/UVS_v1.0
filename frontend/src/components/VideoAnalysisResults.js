import React, { useState, useEffect } from 'react';
import ApiService from '../services/ApiService';
import './VideoAnalysisResults.css';

const VideoAnalysisResults = ({ resultData }) => {
  const [analysisResults, setAnalysisResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (resultData) {
      console.log("Result data received:", resultData);
      
      // YOLO işleme sonuçları mı kontrol et
      if (resultData.processed_video?.url) {
        // YOLO video işleme sonuçlarını göster
        setAnalysisResults([{
          id: resultData.id || "yolo-id",
          frame: 0,
          timestamp: new Date().toISOString(),
          detections: resultData.results?.detection_results?.isg_items || [
            {
              class: 'yolo_mode',
              confidence: 1.0,
              status: 'detected'
            }
          ],
          image_url: resultData.file_info?.path || '/media/test.jpg',
          video_url: resultData.processed_video.url,
          is_yolo: true,
          yolo_result: resultData
        }]);
        setTotalResults(1);
        setHasMore(false);
      }
      // Standalone işleme sonuçları mı kontrol et
      else if (resultData.results) {
        // Standalone video işleme sonuçlarını göster
        setAnalysisResults([{
          id: resultData.id || "standalone-id",
          frame: 0,
          timestamp: new Date().toISOString(),
          detections: resultData.results.detection_results?.isg_items || [
            {
              class: 'standalone_mode',
              confidence: 1.0,
              status: 'detected'
            }
          ],
          image_url: resultData.file_info?.path || '/media/test.jpg',
          is_standalone: true,
          standalone_result: resultData
        }]);
        setTotalResults(1);
        setHasMore(false);
      }
      // Test sonucu veya basit işleme sonucu mu kontrol et
      else if (resultData.testResult || resultData.status === "Başarılı") {
        // Test veya basit işleme sonucunu göster
        setAnalysisResults([{
          id: resultData.id || "test-id",
          frame: 0,
          timestamp: new Date().toISOString(),
          detections: [
            {
              class: 'test_mode',
              confidence: 1.0,
              status: 'detected'
            }
          ],
          image_url: resultData.file_info?.path || '/media/test.jpg',
          is_test: true,
          test_result: resultData
        }]);
        setTotalResults(1);
        setHasMore(false);
      } else if (resultData.processed_image_ids && resultData.processed_image_ids.length > 0) {
        // Normal işleme sonuçlarını göster
        fetchAnalysisResults(resultData.processed_image_ids);
      }
    }
  }, [resultData]);

  const fetchAnalysisResults = async (imageIds) => {
    setLoading(true);
    setError(null);
    
    try {
      // Bu kısımda gerçek API istekleri yapacak şekilde kodlanabilir
      // Şimdilik simüle edilmiş veri kullanacağız
      
      // Gerçek implementasyon için:
      // const promises = imageIds.map(id => ApiService.get(`api/processed-images/${id}/`));
      // const responses = await Promise.all(promises);
      // const results = responses.map(response => response.data);
      
      // Simüle edilmiş veri:
      const simulatedResults = imageIds.map(id => ({
        id: id,
        frame: Math.floor(Math.random() * 1000),
        timestamp: new Date().toISOString(),
        detections: [
          {
            class: 'helmet',
            confidence: Math.random() * 0.5 + 0.5,
            status: Math.random() > 0.3 ? 'detected' : 'missing'
          },
          {
            class: 'safety_glasses',
            confidence: Math.random() * 0.5 + 0.5,
            status: Math.random() > 0.4 ? 'detected' : 'missing'
          },
          {
            class: 'gloves',
            confidence: Math.random() * 0.5 + 0.5,
            status: Math.random() > 0.2 ? 'detected' : 'missing'
          },
          {
            class: 'safety_vest',
            confidence: Math.random() * 0.5 + 0.5,
            status: Math.random() > 0.1 ? 'detected' : 'missing'
          }
        ],
        image_url: `/media/processed/frame_${Math.floor(Math.random() * 1000)}.jpg`
      }));
      
      setAnalysisResults(simulatedResults);
      setTotalResults(simulatedResults.length);
      setHasMore(false); // Tüm sonuçlar yüklendi
      
    } catch (error) {
      console.error('Analiz sonuçları yüklenirken hata oluştu:', error);
      setError('Analiz sonuçları yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.');
    } finally {
      setLoading(false);
    }
  };
  
  const loadMoreResults = () => {
    setCurrentPage(prevPage => prevPage + 1);
    // Burada daha fazla sonuç yüklemek için API isteği yapılabilir
  };
  
  const getEquipmentStatusColor = (status) => {
    return status === 'detected' ? 'status-success' : 'status-danger';
  };
  
  const getEquipmentStatusText = (status) => {
    return status === 'detected' ? 'Tespit Edildi' : 'Eksik';
  };

  if (loading && analysisResults.length === 0) {
    return <div className="loading">Analiz sonuçları yükleniyor...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!resultData || analysisResults.length === 0) {
    return <div className="no-results">Henüz analiz sonucu bulunmuyor.</div>;
  }

  return (
    <div className="video-analysis-results">
      <h3>Video Analiz Sonuçları</h3>
      
      <div className="summary-info">
        <div className="summary-item">
          <span className="summary-label">Toplam Kareler:</span>
          <span className="summary-value">{resultData.total_frames}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">İşlenen Kareler:</span>
          <span className="summary-value">{resultData.processed_frames}</span>
        </div>
      </div>
      
      <div className="results-list">
        {analysisResults.map((result, index) => (
          <div className="result-card" key={result.id}>
            <div className="result-header">
              <span className="result-id">Kare #{result.frame}</span>
              <span className="result-timestamp">{new Date(result.timestamp).toLocaleString()}</span>
            </div>
            
            <div className="result-content">
              <div className="result-image">
                {/* Gerçek uygulamada, API'den dönen resim URL'si kullanılabilir */}
                <div className="image-placeholder">
                  Resim yükleniyor... (ID: {result.id})
                </div>
              </div>
              
              {result.is_yolo ? (
                <div className="test-result-details">
                  <h4>YOLO İşleme Sonuçları</h4>
                  
                  {/* İşlenmiş Video Player */}
                  <div className="processed-video-container">
                    <h5>Tespit Sonuçları Görüntülenmiş Video</h5>
                    <video 
                      controls 
                      className="processed-video-player"
                      src={`http://localhost:8000${result.video_url}`}
                    >
                      Tarayıcınız video oynatmayı desteklemiyor.
                    </video>
                  </div>
                  
                  <div className="test-info">
                    <p><strong>Durum:</strong> {result.yolo_result.status}</p>
                    <p><strong>Mesaj:</strong> {result.yolo_result.message}</p>
                    <p><strong>İşlenen Kare Sayısı:</strong> {result.yolo_result.processed_video.frames_processed}</p>
                    {result.yolo_result.file_info && (
                      <>
                        <p><strong>Dosya Adı:</strong> {result.yolo_result.file_info.name}</p>
                        <p><strong>Boyut:</strong> {(result.yolo_result.file_info.size / (1024 * 1024)).toFixed(2)} MB</p>
                        {result.yolo_result.file_info.path && (
                          <p><strong>Orijinal Dosya Yolu:</strong> {result.yolo_result.file_info.path}</p>
                        )}
                      </>
                    )}
                  </div>
                  
                  <div className="detection-results">
                    <h5>Tespit Edilen Ekipmanlar</h5>
                    <ul className="equipment-list">
                      {result.detections.map((detection, idx) => (
                        <li key={idx} className="equipment-item">
                          <span className="equipment-name">
                            {detection.class === 'helmet' && 'Baret'}
                            {detection.class === 'safety_glasses' && 'Gözlük'}
                            {detection.class === 'gloves' && 'Eldiven'}
                            {detection.class === 'safety_vest' && 'Yelek'}
                            {detection.class === 'person' && 'Kişi'}
                            {detection.class === 'yolo_mode' && 'YOLO MODU'}
                            {!['helmet', 'safety_glasses', 'gloves', 'safety_vest', 'person', 'yolo_mode'].includes(detection.class) && detection.class}
                          </span>
                          <span className="equipment-confidence">
                            {(detection.confidence * 100).toFixed(1)}%
                          </span>
                          <span className={`equipment-status ${getEquipmentStatusColor(detection.status)}`}>
                            {getEquipmentStatusText(detection.status)}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : result.is_standalone ? (
                <div className="test-result-details">
                  <h4>Video İşleme Sonuçları</h4>
                  <div className="test-info">
                    <p><strong>Durum:</strong> {result.standalone_result.status}</p>
                    <p><strong>Mesaj:</strong> {result.standalone_result.message}</p>
                    {result.standalone_result.file_info && (
                      <>
                        <p><strong>Dosya Adı:</strong> {result.standalone_result.file_info.name}</p>
                        <p><strong>Boyut:</strong> {(result.standalone_result.file_info.size / (1024 * 1024)).toFixed(2)} MB</p>
                        {result.standalone_result.file_info.path && (
                          <p><strong>Dosya Yolu:</strong> {result.standalone_result.file_info.path}</p>
                        )}
                      </>
                    )}
                  </div>
                  
                  <div className="detection-results">
                    <h5>Tespit Edilen Ekipmanlar</h5>
                    <ul className="equipment-list">
                      {result.detections.map((detection, idx) => (
                        <li key={idx} className="equipment-item">
                          <span className="equipment-name">
                            {detection.class === 'helmet' && 'Baret'}
                            {detection.class === 'safety_glasses' && 'Gözlük'}
                            {detection.class === 'gloves' && 'Eldiven'}
                            {detection.class === 'safety_vest' && 'Yelek'}
                            {detection.class === 'standalone_mode' && 'BAĞIMSIZ MOD'}
                          </span>
                          <span className="equipment-confidence">
                            {(detection.confidence * 100).toFixed(1)}%
                          </span>
                          <span className={`equipment-status ${getEquipmentStatusColor(detection.status)}`}>
                            {getEquipmentStatusText(detection.status)}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : result.is_test ? (
                <div className="test-result-details">
                  <h4>Test Modu Sonuçları</h4>
                  <div className="test-info">
                    <p><strong>Durum:</strong> {result.test_result.status}</p>
                    <p><strong>Mesaj:</strong> {result.test_result.message}</p>
                    {result.test_result.file_info && (
                      <>
                        <p><strong>Dosya Adı:</strong> {result.test_result.file_info.name}</p>
                        <p><strong>Boyut:</strong> {(result.test_result.file_info.size / (1024 * 1024)).toFixed(2)} MB</p>
                        {result.test_result.file_info.path && (
                          <p><strong>Dosya Yolu:</strong> {result.test_result.file_info.path}</p>
                        )}
                      </>
                    )}
                  </div>
                  <div className="alert alert-info">
                    Bu, test modunda bir yükleme işlemiydi. Ekipman tespiti gerçekleşmedi.
                  </div>
                </div>
              ) : (
                <div className="result-details">
                  <h4>Ekipman Tespiti</h4>
                  <ul className="equipment-list">
                    {result.detections.map((detection, idx) => (
                      <li key={idx} className="equipment-item">
                        <span className="equipment-name">
                          {detection.class === 'helmet' && 'Baret'}
                          {detection.class === 'safety_glasses' && 'Gözlük'}
                          {detection.class === 'gloves' && 'Eldiven'}
                          {detection.class === 'safety_vest' && 'Yelek'}
                          {detection.class === 'test_mode' && 'Test Modu'}
                        </span>
                        <span className="equipment-confidence">
                          {(detection.confidence * 100).toFixed(1)}%
                        </span>
                        <span className={`equipment-status ${getEquipmentStatusColor(detection.status)}`}>
                          {getEquipmentStatusText(detection.status)}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {loading && <div className="loading">Daha fazla sonuç yükleniyor...</div>}
      
      {hasMore && (
        <div className="load-more">
          <button 
            className="load-more-button"
            onClick={loadMoreResults}
            disabled={loading}
          >
            Daha Fazla Yükle
          </button>
        </div>
      )}
    </div>
  );
};

export default VideoAnalysisResults;