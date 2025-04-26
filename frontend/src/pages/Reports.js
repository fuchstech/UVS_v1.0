import React, { useState, useEffect } from 'react';
import ApiService from '../services/ApiService';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReports = async () => {
      try {
        // Gerçek API yerine simüle edilmiş verileri kullanalım
        // const response = await ApiService.get('/api/rapor/reports/');
        const response = { data: ApiService.getSimulatedReports() };
        setReports(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching reports:', error);
        setError('Raporlar yüklenirken bir hata oluştu.');
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  if (loading) {
    return <div className="loading">Raporlar yükleniyor...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="reports-container">
      <h2>Raporlar</h2>
      
      <div className="report-filters">
        <select>
          <option value="all">Tüm Raporlar</option>
          <option value="isg">İSG Raporları</option>
          <option value="productivity">Verimlilik Raporları</option>
          <option value="production">Üretim Raporları</option>
        </select>
        
        <input type="date" />
        
        <button>Filtrele</button>
      </div>
      
      <div className="reports-list">
        {reports.length === 0 ? (
          <p>Hiç rapor bulunamadı.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Rapor Adı</th>
                <th>Oluşturma Tarihi</th>
                <th>Tür</th>
                <th>İşlemler</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((report) => (
                <tr key={report.id}>
                  <td>{report.title}</td>
                  <td>{new Date(report.created_at).toLocaleDateString()}</td>
                  <td>{report.report_type}</td>
                  <td>
                    <button>Görüntüle</button>
                    <button>İndir</button>
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

export default Reports;