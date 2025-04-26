import React, { useState } from 'react';
import ApiService from '../services/ApiService';
import './VideoUpload.css';

const VideoUpload = ({ cameraId, onUploadSuccess, onUploadError }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [sampleRate, setSampleRate] = useState(30);
  const [uploadError, setUploadError] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type.includes('video/')) {
        setSelectedFile(file);
        setUploadError(null);
      } else {
        setSelectedFile(null);
        setUploadError('Lütfen geçerli bir video dosyası seçin.');
      }
    }
  };

  const handleSampleRateChange = (event) => {
    setSampleRate(parseInt(event.target.value));
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError('Lütfen bir video dosyası seçin.');
      return;
    }

    if (!cameraId) {
      setUploadError('Kamera ID gerekli.');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setUploadError(null);

    const formData = new FormData();
    formData.append('video', selectedFile);
    formData.append('camera_id', cameraId);
    formData.append('sample_rate', sampleRate);

    try {
      // Simulated progress updates
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

      console.log('Video yükleme isteği başladı. Kamera ID:', cameraId);
      console.log('Video boyutu:', (selectedFile.size / (1024 * 1024)).toFixed(2), 'MB');
      
      try {
        const response = await ApiService.postFormData('api/isg/process-video/', formData);
        console.log('Video yükleme yanıtı:', response);
        
        clearInterval(progressInterval);
        setUploadProgress(100);
        setIsUploading(false);
        setSelectedFile(null);
        
        if (onUploadSuccess) {
          onUploadSuccess(response.data);
        }
      } catch (error) {
        console.error('Video yükleme hatası:', error);
        clearInterval(progressInterval);
        setIsUploading(false);
        
        // Hata detaylarını elde et
        const errorMessage = error.response?.data?.detail || 
                             error.message || 
                             'Video yüklenirken bir hata oluştu.';
                             
        console.error('Hata detayı:', errorMessage);
        setUploadError(`Hata: ${errorMessage}`);
        
        if (onUploadError) {
          onUploadError(errorMessage);
        }
      }
    } catch (e) {
      console.error('Genel hata:', e);
      setIsUploading(false);
      setUploadError(`Beklenmeyen bir hata oluştu: ${e.message}`);
      
      if (onUploadError) {
        onUploadError(e.message);
      }
    }
  };

  return (
    <div className="video-upload-container">
      <h3>Video Yükleme</h3>
      <p>
        Ekipman tespiti için bilgisayarınızdan bir video yükleyin.
      </p>
      
      <div className="upload-form">
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
        
        <div className="form-group">
          <label htmlFor="sample-rate">Örnekleme Hızı (Her kaç karede bir işlensin):</label>
          <select
            id="sample-rate"
            value={sampleRate}
            onChange={handleSampleRateChange}
            disabled={isUploading}
          >
            <option value="1">Her kare (Çok yavaş)</option>
            <option value="5">Her 5 kare</option>
            <option value="10">Her 10 kare</option>
            <option value="15">Her 15 kare</option>
            <option value="30">Her 30 kare (Önerilen)</option>
            <option value="60">Her 60 kare (Hızlı)</option>
          </select>
          <p className="help-text">
            Daha düşük değerler daha hassas analiz sağlar ancak işleme süresi uzar.
          </p>
        </div>
        
        {uploadError && <div className="upload-error">{uploadError}</div>}
        
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
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
          >
            Video Yükle ve İşle
          </button>
        )}
      </div>
    </div>
  );
};

export default VideoUpload;