import React, { useState, useEffect } from 'react';
import ApiService from '../../services/ApiService';
import './isg.css';

const DangerZones = () => {
  const [zones, setZones] = useState([]);
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Gerçek API'ye bağlanmak yerine simüle edilmiş veri kullanıyoruz
    const fetchData = async () => {
      try {
        // Simüle edilmiş tehlikeli bölgeler
        const simulatedZones = [
          {
            id: 1,
            name: 'Makine Odası',
            description: 'Tehlikeli makinelerin bulunduğu alan',
            level: 'high',
            status: 'active',
            camera_ids: [1, 2]
          },
          {
            id: 2,
            name: 'Kimyasal Depo',
            description: 'Tehlikeli kimyasalların depolandığı alan',
            level: 'critical',
            status: 'active',
            camera_ids: [3]
          },
          {
            id: 3,
            name: 'Elektrik Panosu',
            description: 'Yüksek gerilim panolarının bulunduğu alan',
            level: 'medium',
            status: 'active',
            camera_ids: [4]
          },
          {
            id: 4,
            name: 'Forklift Yolu',
            description: 'Forklift ve araçların geçiş alanı',
            level: 'low',
            status: 'inactive',
            camera_ids: [5, 6]
          }
        ];
        
        // Simüle edilmiş ihlaller
        const simulatedViolations = [
          {
            id: 1,
            zone_id: 1,
            zone_name: 'Makine Odası',
            timestamp: '2025-04-26T10:15:30Z',
            person_id: 'E-12345',
            person_name: 'Ahmet Yılmaz',
            camera_name: 'Kamera-1',
            image_url: 'https://via.placeholder.com/150',
            status: 'open'
          },
          {
            id: 2,
            zone_id: 2,
            zone_name: 'Kimyasal Depo',
            timestamp: '2025-04-26T09:45:12Z',
            person_id: 'E-23456',
            person_name: 'Mehmet Kaya',
            camera_name: 'Kamera-3',
            image_url: 'https://via.placeholder.com/150',
            status: 'resolved'
          },
          {
            id: 3,
            zone_id: 1,
            zone_name: 'Makine Odası',
            timestamp: '2025-04-25T16:30:45Z',
            person_id: 'E-34567',
            person_name: 'Ayşe Demir',
            camera_name: 'Kamera-2',
            image_url: 'https://via.placeholder.com/150',
            status: 'open'
          }
        ];
        
        setZones(simulatedZones);
        setViolations(simulatedViolations);
        setLoading(false);
      } catch (error) {
        console.error('Tehlikeli alan verileri yüklenirken hata oluştu:', error);
        setError('Tehlikeli alan verileri yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="loading">Yükleniyor...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  // Tehlike seviyelerine göre sınıf belirleme
  const getDangerLevelClass = (level) => {
    switch (level) {
      case 'critical': return 'danger-critical';
      case 'high': return 'danger-high';
      case 'medium': return 'danger-medium';
      case 'low': return 'danger-low';
      default: return '';
    }
  };

  return (
    <div className="danger-zones-container">
      <h2>Tehlikeli Alan Kontrolü</h2>
      <p className="module-description">
        Bu modül, tanımlanmış tehlikeli alanlardaki yetkisiz girişleri tespit eder ve raporlar.
      </p>

      <div className="zones-list">
        <h3>Tanımlı Tehlikeli Alanlar</h3>
        <table>
          <thead>
            <tr>
              <th>Alan Adı</th>
              <th>Açıklama</th>
              <th>Tehlike Seviyesi</th>
              <th>Durum</th>
              <th>Kamera Sayısı</th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {zones.map((zone) => (
              <tr key={zone.id}>
                <td>{zone.name}</td>
                <td>{zone.description}</td>
                <td>
                  <span className={`tag ${getDangerLevelClass(zone.level)}`}>
                    {zone.level === 'critical' && 'Kritik'}
                    {zone.level === 'high' && 'Yüksek'}
                    {zone.level === 'medium' && 'Orta'}
                    {zone.level === 'low' && 'Düşük'}
                  </span>
                </td>
                <td>
                  <span className={`tag ${zone.status === 'active' ? 'tag-active' : 'tag-inactive'}`}>
                    {zone.status === 'active' ? 'Aktif' : 'Pasif'}
                  </span>
                </td>
                <td>{zone.camera_ids.length}</td>
                <td>
                  <button className="btn btn-small">Düzenle</button>
                  <button className="btn btn-small">Kameralar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="violations-list">
        <h3>Son İhlaller</h3>
        <table>
          <thead>
            <tr>
              <th>Alan</th>
              <th>Tarih/Saat</th>
              <th>Personel</th>
              <th>Kamera</th>
              <th>Durum</th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {violations.map((violation) => (
              <tr key={violation.id}>
                <td>{violation.zone_name}</td>
                <td>{new Date(violation.timestamp).toLocaleString('tr-TR')}</td>
                <td>{violation.person_name} ({violation.person_id})</td>
                <td>{violation.camera_name}</td>
                <td>
                  <span className={`tag ${violation.status === 'open' ? 'tag-open' : 'tag-resolved'}`}>
                    {violation.status === 'open' ? 'Açık' : 'Çözüldü'}
                  </span>
                </td>
                <td>
                  <button className="btn btn-small">Detay</button>
                  {violation.status === 'open' && (
                    <button className="btn btn-small btn-success">Çözüldü İşaretle</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="action-buttons">
        <button className="btn btn-primary">
          <i className="fas fa-plus"></i> Yeni Tehlikeli Alan Tanımla
        </button>
        <button className="btn">
          <i className="fas fa-file-export"></i> İhlal Raporu Oluştur
        </button>
      </div>
    </div>
  );
};

export default DangerZones;
