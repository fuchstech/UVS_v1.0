import axios from 'axios';

const API_URL = 'http://localhost:8000/api/';

const AuthService = {
  login: async (username, password) => {
    try {
      const response = await axios.post(`${API_URL}auth/login/`, {
        username,
        password
      }, {
        headers: {
          'X-API-KEY': '5f46f9d0-ca57-4c39-a104-af1bad3022ea'
        }
      });
      
      if (response.data.token) {
        localStorage.setItem('user', JSON.stringify(response.data));
      }
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  logout: () => {
    localStorage.removeItem('user');
  },
  
  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      return JSON.parse(userStr);
    }
    return null;
  },
  
  // Simüle edilmiş oturum açma (backend olmadan test için)
  simulateLogin: (username, password) => {
    // Test kullanıcısı
    if (username === 'admin' && password === 'admin123') {
      const userData = {
        id: 1,
        username: 'admin',
        name: 'Admin Kullanıcı',
        email: 'admin@kapadokya.com',
        role: 'Yönetici',
        token: 'simulated-jwt-token'
      };
      
      localStorage.setItem('user', JSON.stringify(userData));
      return userData;
    }
    
    throw new Error('Geçersiz kullanıcı adı veya şifre');
  }
};

export default AuthService;