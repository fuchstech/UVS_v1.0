import React, { useState, useEffect } from 'react';
import ApiService from '../../services/ApiService';

const EquipmentControl = () => {
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Gerçek API'ye bağlanmak yerine simüle edilmiş veri kullanıyoruz
    const fetchEquipment = async () => {
      try {
        // Simüle edilmiş veriler
        const simulatedData = [
          {
            id: 1,
            name: 'Baret',
            description: 'Çalışan kask koruması',
            required: true,
            detection_class: 'helmet'
          },
          {
            id: 2,
            name: 'Gözlük',
            description: 'Koruyucu gözlük',
            required: true,
            detection_class: 'safety_glasses'
          },
          {
            id: 3,
            name: 'Eldiven',
            description: 'Koruyucu iş eldiveni',
            required: true,
            detection_class: 'gloves'
          },
          {
            id: 4,
            name: 'Yelek',
            description: 'Reflektörlü güvenlik yeleği',
            required: true,
            detection_class: 'safety_vest'
          }
        ];
        
        setEquipment(simulatedData);
        setLoading(false);
      } catch (error) {
        console.error('Ekipman verileri yüklenirken hata oluştu:', error);
        setError('Ekipman verileri yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.');
        setLoading(false);
      }
    };

    fetchEquipment();
  }, []);

  if (loading) {
    return <div className="loading">Yükleniyor...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="equipment-control-container">
      <h2>İSG Ekipman Kontrolü</h2>
      <p className="module-description">
        Bu modül, çalışanların iş güvenliği ekipmanlarını (baret, gözlük, eldiven vb.) 
        kullanıp kullanmadıklarını YOLOv11 algoritması ile tespit eder.
      </p>

      <div className="equipment-list">
        <h3>Gerekli Güvenlik Ekipmanları</h3>
        <table>
          <thead>
            <tr>
              <th>Ekipman</th>
              <th>Açıklama</th>
              <th>Gereklilik</th>
              <th>Tespit Sınıfı</th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {equipment.map((item) => (
              <tr key={item.id}>
                <td>{item.name}</td>
                <td>{item.description}</td>
                <td>
                  <span className={`tag ${item.required ? 'tag-required' : 'tag-optional'}`}>
                    {item.required ? 'Zorunlu' : 'Opsiyonel'}
                  </span>
                </td>
                <td><code>{item.detection_class}</code></td>
                <td>
                  <button className="btn btn-small">Düzenle</button>
                  <button className="btn btn-small btn-danger">Sil</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="equipment-stats">
        <h3>Ekipman Kullanım İstatistikleri</h3>
        <div className="stats-cards">
          <div className="stats-card">
            <h4>Baret Kullanım Oranı</h4>
            <div className="stats-value">%86</div>
            <div className="stats-trend stats-up">
              <i className="fas fa-arrow-up"></i> %4 artış
            </div>
          </div>
          
          <div className="stats-card">
            <h4>Gözlük Kullanım Oranı</h4>
            <div className="stats-value">%72</div>
            <div className="stats-trend stats-down">
              <i className="fas fa-arrow-down"></i> %3 azalış
            </div>
          </div>
          
          <div className="stats-card">
            <h4>Eldiven Kullanım Oranı</h4>
            <div className="stats-value">%91</div>
            <div className="stats-trend stats-up">
              <i className="fas fa-arrow-up"></i> %7 artış
            </div>
          </div>
          
          <div className="stats-card">
            <h4>Yelek Kullanım Oranı</h4>
            <div className="stats-value">%94</div>
            <div className="stats-trend stats-stable">
              <i className="fas fa-equals"></i> Değişim yok
            </div>
          </div>
        </div>
      </div>
      
      <div className="action-buttons">
        <button className="btn btn-primary">
          <i className="fas fa-plus"></i> Yeni Ekipman Ekle
        </button>
        <button className="btn">
          <i className="fas fa-file-export"></i> Rapor Oluştur
        </button>
      </div>
    </div>
  );
};

export default EquipmentControl;
