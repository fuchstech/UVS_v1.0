import React, { useState, useEffect } from 'react';
import ApiService from '../../services/ApiService';

const WorkerSafety = () => {
  const [workers, setWorkers] = useState([]);
  const [violations, setViolations] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Gerçek API'ye bağlanmak yerine simüle edilmiş veri kullanıyoruz
    const fetchData = async () => {
      try {
        // Simüle edilmiş işçi verileri
        const simulatedWorkers = [
          {
            id: 'E-12345',
            name: 'Ahmet Yılmaz',
            department: 'Üretim',
            safety_score: 85,
            violation_count: 3,
            safety_status: 'good'
          },
          {
            id: 'E-23456',
            name: 'Mehmet Kaya',
            department: 'Montaj',
            safety_score: 92,
            violation_count: 1,
            safety_status: 'excellent'
          },
          {
            id: 'E-34567',
            name: 'Ayşe Demir',
            department: 'Üretim',
            safety_score: 78,
            violation_count: 5,
            safety_status: 'warning'
          },
          {
            id: 'E-45678',
            name: 'Fatma Şahin',
            department: 'Depo',
            safety_score: 65,
            violation_count: 8,
            safety_status: 'danger'
          },
          {
            id: 'E-56789',
            name: 'Ali Öztürk',
            department: 'Montaj',
            safety_score: 95,
            violation_count: 0,
            safety_status: 'excellent'
          }
        ];
        
        // Simüle edilmiş ihlal verileri
        const simulatedViolations = [
          {
            id: 101,
            worker_id: 'E-12345',
            worker_name: 'Ahmet Yılmaz',
            violation_type: 'missing_helmet',
            timestamp: '2025-04-26T10:15:30Z',
            location: 'Üretim Alanı',
            camera_name: 'Kamera-1',
            status: 'open'
          },
          {
            id: 102,
            worker_id: 'E-34567',
            worker_name: 'Ayşe Demir',
            violation_type: 'danger_zone',
            timestamp: '2025-04-26T09:45:12Z',
            location: 'Makine Odası',
            camera_name: 'Kamera-3',
            status: 'resolved'
          },
          {
            id: 103,
            worker_id: 'E-45678',
            worker_name: 'Fatma Şahin',
            violation_type: 'missing_gloves',
            timestamp: '2025-04-25T16:30:45Z',
            location: 'Depo Alanı',
            camera_name: 'Kamera-5',
            status: 'open'
          }
        ];
        
        // Simüle edilmiş istatistikler
        const simulatedStats = {
          total_workers: 42,
          total_violations: 86,
          open_violations: 24,
          average_safety_score: 83,
          department_stats: {
            "Üretim": {
              worker_count: 18,
              violation_count: 38,
              average_score: 81
            },
            "Montaj": {
              worker_count: 12,
              violation_count: 22,
              average_score: 87
            },
            "Depo": {
              worker_count: 8,
              violation_count: 16,
              average_score: 76
            },
            "Kalite Kontrol": {
              worker_count: 4,
              violation_count: 10,
              average_score: 88
            }
          }
        };
        
        setWorkers(simulatedWorkers);
        setViolations(simulatedViolations);
        setStats(simulatedStats);
        setLoading(false);
      } catch (error) {
        console.error('İşçi güvenliği verileri yüklenirken hata oluştu:', error);
        setError('İşçi güvenliği verileri yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.');
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

  // Güvenlik skoruna göre sınıf belirleme
  const getSafetyClass = (status) => {
    switch (status) {
      case 'excellent': return 'safety-excellent';
      case 'good': return 'safety-good';
      case 'warning': return 'safety-warning';
      case 'danger': return 'safety-danger';
      default: return '';
    }
  };

  // İhlal tipine göre isim belirleme
  const getViolationTypeName = (type) => {
    switch (type) {
      case 'missing_helmet': return 'Baret Eksikliği';
      case 'missing_gloves': return 'Eldiven Eksikliği';
      case 'missing_glasses': return 'Gözlük Eksikliği';
      case 'missing_vest': return 'Yelek Eksikliği';
      case 'danger_zone': return 'Tehlikeli Alan İhlali';
      case 'unauthorized_entry': return 'Yetkisiz Giriş';
      default: return type;
    }
  };

  return (
    <div className="worker-safety-container">
      <h2>İşçi Güvenliği</h2>
      <p className="module-description">
        Bu modül, çalışanların iş güvenliği performansını takip eder ve ihlalleri raporlar.
      </p>

      <div className="safety-stats">
        <div className="stats-cards">
          <div className="stats-card">
            <h4>Toplam Çalışan</h4>
            <div className="stats-value">{stats.total_workers}</div>
          </div>
          
          <div className="stats-card">
            <h4>Toplam İhlal</h4>
            <div className="stats-value">{stats.total_violations}</div>
          </div>
          
          <div className="stats-card">
            <h4>Açık İhlaller</h4>
            <div className="stats-value">{stats.open_violations}</div>
          </div>
          
          <div className="stats-card">
            <h4>Ortalama Güvenlik Skoru</h4>
            <div className="stats-value">{stats.average_safety_score}%</div>
          </div>
        </div>
      </div>
      
      <div className="workers-list">
        <h3>Çalışan Güvenlik Durumları</h3>
        <table>
          <thead>
            <tr>
              <th>Personel ID</th>
              <th>İsim</th>
              <th>Departman</th>
              <th>Güvenlik Skoru</th>
              <th>İhlal Sayısı</th>
              <th>Durum</th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {workers.map((worker) => (
              <tr key={worker.id}>
                <td>{worker.id}</td>
                <td>{worker.name}</td>
                <td>{worker.department}</td>
                <td>{worker.safety_score}%</td>
                <td>{worker.violation_count}</td>
                <td>
                  <span className={`tag ${getSafetyClass(worker.safety_status)}`}>
                    {worker.safety_status === 'excellent' && 'Mükemmel'}
                    {worker.safety_status === 'good' && 'İyi'}
                    {worker.safety_status === 'warning' && 'Uyarı'}
                    {worker.safety_status === 'danger' && 'Tehlike'}
                  </span>
                </td>
                <td>
                  <button className="btn btn-small">Detay</button>
                  <button className="btn btn-small">İhlaller</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="violations-list">
        <h3>Son Güvenlik İhlalleri</h3>
        <table>
          <thead>
            <tr>
              <th>Personel</th>
              <th>İhlal Tipi</th>
              <th>Tarih/Saat</th>
              <th>Konum</th>
              <th>Durum</th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {violations.map((violation) => (
              <tr key={violation.id}>
                <td>{violation.worker_name} ({violation.worker_id})</td>
                <td>{getViolationTypeName(violation.violation_type)}</td>
                <td>{new Date(violation.timestamp).toLocaleString('tr-TR')}</td>
                <td>{violation.location}</td>
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
          <i className="fas fa-file-export"></i> Güvenlik Raporu Oluştur
        </button>
        <button className="btn">
          <i className="fas fa-envelope"></i> İhlal Bildirimi Gönder
        </button>
      </div>
    </div>
  );
};

export default WorkerSafety;
