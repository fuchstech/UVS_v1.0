import React, { useState, useEffect } from 'react';
import './Header.css';

const Header = ({ user, onLogout }) => {
  const [currentDate, setCurrentDate] = useState('');
  const [currentTime, setCurrentTime] = useState('');
  
  useEffect(() => {
    // Update date and time on component mount
    updateDateTime();
    
    // Set up interval to update time every minute
    const interval = setInterval(updateDateTime, 60000);
    
    // Clean up interval on component unmount
    return () => clearInterval(interval);
  }, []);
  
  const updateDateTime = () => {
    const now = new Date();
    
    // Format date: 26 Nisan 2025
    const options = { day: 'numeric', month: 'long', year: 'numeric' };
    setCurrentDate(now.toLocaleDateString('tr-TR', options));
    
    // Format time: 14:30
    setCurrentTime(now.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }));
  };
  
  const handleLogout = () => {
    // Show confirmation dialog
    if (window.confirm('Çıkış yapmak istediğinize emin misiniz?')) {
      onLogout();
    }
  };
  
  return (
    <header className="main-header">
      <div className="header-left">
        <button className="mobile-menu-toggle">
          <i className="fas fa-bars"></i>
        </button>
        <div className="breadcrumbs">
          <span>Ana Sayfa</span>
        </div>
      </div>
      
      <div className="header-center">
        <div className="search-container">
          <input type="text" placeholder="Ara..." />
          <button className="search-button">
            <i className="fas fa-search"></i>
          </button>
        </div>
      </div>
      
      <div className="header-right">
        <div className="date-time">
          <span className="date">{currentDate}</span>
          <span className="time">{currentTime}</span>
        </div>
        
        <div className="header-actions">
          <button className="action-button notification-button">
            <i className="fas fa-bell"></i>
            <span className="notification-badge">3</span>
          </button>
          
          <button className="action-button">
            <i className="fas fa-cog"></i>
          </button>
          
          <div className="user-dropdown">
            <button className="user-button">
              <img 
                src={user?.avatar || "https://via.placeholder.com/32"} 
                alt="Kullanıcı" 
                className="user-avatar-small"
              />
              <span>{user?.name || "Kullanıcı"}</span>
              <i className="fas fa-chevron-down"></i>
            </button>
            
            <div className="dropdown-menu">
              <a href="#"><i className="fas fa-user"></i> Profil</a>
              <a href="#"><i className="fas fa-cog"></i> Ayarlar</a>
              <a href="#" onClick={handleLogout}><i className="fas fa-sign-out-alt"></i> Çıkış</a>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
