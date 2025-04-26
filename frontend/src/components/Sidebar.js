import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = ({ user }) => {
  return (
    <nav className="sidebar">
      <div className="logo">
        <h2>Kapadokya AI</h2>
        <p>Üretim Verimlilik Sistemi</p>
      </div>
      
      <ul className="menu">
        <li>
          <NavLink to="/" exact activeclassname="active">
            <i className="fas fa-home"></i> Ana Sayfa
          </NavLink>
        </li>
        <li>
          <NavLink to="/tasks" activeclassname="active">
            <i className="fas fa-tasks"></i> Görev Takibi
          </NavLink>
        </li>
        <li>
          <NavLink to="/alerts" activeclassname="active">
            <i className="fas fa-bell"></i> Alarmlar 
            <span className="alert-badge">2</span>
          </NavLink>
        </li>
        <li>
          <NavLink to="/feedback" activeclassname="active">
            <i className="fas fa-comment"></i> Geri Bildirim
          </NavLink>
        </li>
        <li>
          <NavLink to="/reports" activeclassname="active">
            <i className="fas fa-chart-bar"></i> Raporlar
          </NavLink>
        </li>
      </ul>
      
      <div className="sidebar-section">
        <h3>İSG Modülleri</h3>
        <ul className="submenu">
          <li><NavLink to="/isg/equipment"><i className="fas fa-hard-hat"></i> Ekipman Kontrolü</NavLink></li>
          <li><NavLink to="/isg/danger-zones"><i className="fas fa-exclamation-triangle"></i> Tehlikeli Alan</NavLink></li>
          <li><NavLink to="/isg/worker-safety"><i className="fas fa-user-shield"></i> İşçi Güvenliği</NavLink></li>
        </ul>
      </div>
      
      <div className="sidebar-section">
        <h3>Verimlilik</h3>
        <ul className="submenu">
          <li><a href="#"><i className="fas fa-user-clock"></i> İşçi Takibi</a></li>
          <li><a href="#"><i className="fas fa-map"></i> Hareket Haritası</a></li>
          <li><a href="#"><i className="fas fa-chart-line"></i> Verimlilik Analizi</a></li>
        </ul>
      </div>
      
      <div className="sidebar-section">
        <h3>Üretim</h3>
        <ul className="submenu">
          <li><a href="#"><i className="fas fa-boxes"></i> Ürün Sayımı</a></li>
          <li><a href="#"><i className="fas fa-check-circle"></i> Kalite Kontrol</a></li>
        </ul>
      </div>
      
      <div className="user-info">
        <img 
          src={user?.avatar || "https://via.placeholder.com/40"} 
          alt="Kullanıcı" 
          className="user-avatar"
        />
        <div className="user-details">
          <span className="user-name">{user?.name || "Kullanıcı"}</span>
          <span className="user-role">{user?.role || "Yetkili"}</span>
        </div>
      </div>
    </nav>
  );
};

export default Sidebar;
