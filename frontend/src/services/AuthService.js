import ApiService from './ApiService';

const AuthService = {
  login: async (username, password) => {
    try {
      const response = await ApiService.post('/auth/login/', {
        username,
        password,
      });
      
      // Store token in localStorage
      localStorage.setItem('token', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      return response.user;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  register: async (userData) => {
    return ApiService.post('/auth/register/', userData);
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      return JSON.parse(userStr);
    }
    return null;
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },

  refreshToken: async () => {
    try {
      const response = await ApiService.post('/auth/token/refresh/');
      localStorage.setItem('token', response.token);
      return response.token;
    } catch (error) {
      console.error('Token refresh error:', error);
      // If refresh fails, logout
      AuthService.logout();
      throw error;
    }
  },

  updateProfile: async (userData) => {
    try {
      const response = await ApiService.put('/auth/profile/', userData);
      
      // Update stored user data
      const currentUser = AuthService.getCurrentUser();
      const updatedUser = { ...currentUser, ...response };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      
      return updatedUser;
    } catch (error) {
      console.error('Profile update error:', error);
      throw error;
    }
  },

  changePassword: async (currentPassword, newPassword) => {
    return ApiService.post('/auth/change-password/', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },
};

export default AuthService;
