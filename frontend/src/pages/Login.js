import React, { useState } from 'react';
import AuthService from '../services/AuthService';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Gerçek API'yi kullanmak yerine simüle edilmiş oturumu kullanaralım
      // const userData = await AuthService.login(username, password);
      const userData = await AuthService.simulateLogin(username, password);
      onLogin(userData);
    } catch (error) {
      setError('Giriş başarısız. Kullanıcı adı veya şifre hatalı.');
      console.error('Login failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-form-box">
        <h2>Kapadokya AI - Üretim Verimlilik Sistemi</h2>
        <div className="login-info">
          <p><strong>Test Girişi:</strong> Bu simüle edilmiş ortamda giriş yapmak için:</p>
          <p>Kullanıcı Adı: <strong>admin</strong></p>
          <p>Şifre: <strong>admin123</strong></p>
        </div>
        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-group">
            <label htmlFor="username">Kullanıcı Adı</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Şifre</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          
          <button type="submit" disabled={loading} className="login-button">
            {loading ? 'Giriş Yapılıyor...' : 'Giriş Yap'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;