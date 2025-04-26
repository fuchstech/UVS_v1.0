import React, { useState, useEffect } from 'react';
import ApiService from '../services/ApiService';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        // Gerçek API yerine simüle edilmiş verileri kullanalım
        // const response = await ApiService.get('/api/isg/alerts/');
        const response = { data: ApiService.getSimulatedAlerts() };
        setAlerts(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching alerts:', error);
        setError('Uyarılar yüklenirken bir hata oluştu.');
        setLoading(false);
      }
    };

    fetchAlerts();
  }, []);

  if (loading) {
    return <div className="loading">Uyarılar yükleniyor...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="alerts-container">
      <h2>Uyarılar ve İhlaller</h2>
      
      <div className="alert-filters">
        <select>
          <option value="all">Tüm Uyarılar</option>
          <option value="open">Açık Uyarılar</option>
          <option value="resolved">Çözülmüş Uyarılar</option>
          <option value="critical">Kritik Uyarılar</option>
        </select>
        
        <input type="date" />
        
        <button>Filtrele</button>
      </div>
      
      <div className="alerts-list">
        {alerts.length === 0 ? (
          <p>Hiç uyarı bulunamadı.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Uyarı Türü</th>
                <th>Kamera</th>
                <th>Tarih/Saat</th>
                <th>Durum</th>
                <th>Öncelik</th>
                <th>İşlemler</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((alert) => (
                <tr key={alert.id}>
                  <td>{alert.alert_type}</td>
                  <td>{alert.camera_name}</td>
                  <td>{new Date(alert.timestamp).toLocaleString()}</td>
                  <td>
                    <span className={`status status-${alert.status.toLowerCase()}`}>
                      {alert.status}
                    </span>
                  </td>
                  <td>
                    <span className={`priority priority-${alert.priority.toLowerCase()}`}>
                      {alert.priority}
                    </span>
                  </td>
                  <td>
                    <button>Detay</button>
                    <button>Çözüldü</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Alerts;