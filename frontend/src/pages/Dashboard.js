import React from 'react';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      <div className="dashboard-content">
        <div className="dashboard-card">
          <h3>İSG Durumu</h3>
          <p>Günlük İSG ihlalleri: 3</p>
          <p>Açık uyarılar: 1</p>
        </div>
        <div className="dashboard-card">
          <h3>Verimlilik Metrikleri</h3>
          <p>Ortalama verimlilik: %82</p>
          <p>Hedef: %85</p>
        </div>
        <div className="dashboard-card">
          <h3>Üretim Takibi</h3>
          <p>Bugünkü üretim: 540 parça</p>
          <p>Hedef: 600 parça</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;