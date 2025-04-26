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
    if (resultData && resultData.processed_image_ids && resultData.processed_image_ids.length > 0) {
      fetchAnalysisResults(resultData.processed_image_ids);
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