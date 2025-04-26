import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add a request interceptor to include auth token
apiClient.interceptors.request.use(
  config => {
    const user = JSON.parse(localStorage.getItem('user'));
    if (user && user.token) {
      config.headers['Authorization'] = `Token ${user.token}`;
    }
    // API key ekleme
    config.headers['X-API-KEY'] = '5f46f9d0-ca57-4c39-a104-af1bad3022ea';
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle common errors
apiClient.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    // Handle 401 Unauthorized
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const ApiService = {
  get: async (url, params = {}) => {
    try {
      const response = await apiClient.get(url, { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  post: async (url, data = {}) => {
    try {
      const response = await apiClient.post(url, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  put: async (url, data = {}) => {
    try {
      const response = await apiClient.put(url, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  delete: async (url) => {
    try {
      const response = await apiClient.delete(url);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  postFormData: async (url, formData) => {
    try {
      // URL başına / ekleyin
      const fullUrl = url.startsWith('/') ? `${API_URL}${url}` : `${API_URL}/${url}`;
      console.log('Gönderilen tam URL:', fullUrl);
      
      // Content-Type header'a gerek yok, FormData sınırı otomatik oluşturur
      const response = await axios.post(fullUrl, formData, {
        headers: {
          'X-API-KEY': '5f46f9d0-ca57-4c39-a104-af1bad3022ea',
          'Authorization': (() => {
            const user = JSON.parse(localStorage.getItem('user'));
            return user && user.token ? `Token ${user.token}` : '';
          })()
        }
      });
      return response;
    } catch (error) {
      console.error('postFormData hata:', error);
      throw error;
    }
  },
  
  // Simüle edilmiş veri fonksiyonları (geliştirme aşamasında kullanmak için)
  
  // Örnek: Simüle edilmiş uyarılar
  getSimulatedAlerts: () => {
    return [
      {
        id: 1,
        alert_type: 'Baret İhlali',
        camera_name: 'Kamera-1 (Üretim Alanı)',
        timestamp: new Date().toISOString(),
        status: 'Açık',
        priority: 'Yüksek'
      },
      {
        id: 2,
        alert_type: 'Tehlikeli Alan Girişi',
        camera_name: 'Kamera-3 (Depo)',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        status: 'İnceleniyor',
        priority: 'Orta'
      },
      {
        id: 3,
        alert_type: 'Eldiven İhlali',
        camera_name: 'Kamera-2 (Montaj Hattı)',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        status: 'Çözüldü',
        priority: 'Düşük'
      }
    ];
  },
  
  // Örnek: Simüle edilmiş görevler
  getSimulatedTasks: () => {
    return [
      {
        id: 1,
        title: 'Montaj Hattı Kontrolü',
        assigned_to: 'Ahmet Yılmaz',
        status: 'Devam Ediyor',
        start_date: new Date().toISOString(),
        end_date: null
      },
      {
        id: 2,
        title: 'Kamera Kurulumu',
        assigned_to: 'Mehmet Öz',
        status: 'Tamamlandı',
        start_date: new Date(Date.now() - 86400000).toISOString(),
        end_date: new Date().toISOString()
      },
      {
        id: 3,
        title: 'YOLOv11 Model Güncellemesi',
        assigned_to: 'Ayşe Demir',
        status: 'Beklemede',
        start_date: new Date(Date.now() + 86400000).toISOString(),
        end_date: null
      }
    ];
  },
  
  // Örnek: Simüle edilmiş raporlar
  getSimulatedReports: () => {
    return [
      {
        id: 1,
        title: 'Haftalık İSG Raporu',
        created_at: new Date().toISOString(),
        report_type: 'İSG'
      },
      {
        id: 2,
        title: 'Aylık Verimlilik Raporu',
        created_at: new Date(Date.now() - 604800000).toISOString(),
        report_type: 'Verimlilik'
      },
      {
        id: 3,
        title: 'Üretim Hattı Analizi',
        created_at: new Date(Date.now() - 1209600000).toISOString(),
        report_type: 'Üretim'
      }
    ];
  }
};

export default ApiService;