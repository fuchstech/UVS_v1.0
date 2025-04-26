import ApiService from './ApiService';

const ISGService = {
  // Safety equipment management
  getEquipment: () => {
    return ApiService.get('/isg/equipment/');
  },

  getEquipmentById: (id) => {
    return ApiService.get(`/isg/equipment/${id}/`);
  },

  createEquipment: (equipmentData) => {
    return ApiService.post('/isg/equipment/', equipmentData);
  },

  updateEquipment: (id, equipmentData) => {
    return ApiService.put(`/isg/equipment/${id}/`, equipmentData);
  },

  deleteEquipment: (id) => {
    return ApiService.delete(`/isg/equipment/${id}/`);
  },

  // Safety violations
  getViolations: (params = {}) => {
    return ApiService.get('/isg/violations/', params);
  },

  getViolationById: (id) => {
    return ApiService.get(`/isg/violations/${id}/`);
  },

  resolveViolation: (id, notes = '') => {
    return ApiService.post(`/isg/resolve-violation/${id}/`, { notes });
  },

  // Safety reports
  getSafetyReports: (params = {}) => {
    return ApiService.get('/isg/reports/', params);
  },

  getSafetyReportById: (id) => {
    return ApiService.get(`/isg/reports/${id}/`);
  },

  generateSafetyReport: (date) => {
    return ApiService.post('/isg/reports/generate_report/', { date });
  },

  // Image processing for safety
  processImage: (cameraId, imageFile, onProgress) => {
    const formData = new FormData();
    formData.append('camera_id', cameraId);
    formData.append('image', imageFile);

    return ApiService.uploadFile('/isg/process-image/', formData, onProgress);
  },

  // Camera streams
  getCameras: (type = 'isg') => {
    return ApiService.get('/cameras/', { type });
  },

  // Safety zones
  getDangerZones: (cameraId) => {
    return ApiService.get('/zones/', { 
      camera: cameraId,
      is_danger: true 
    });
  },

  createZone: (zoneData) => {
    return ApiService.post('/zones/', zoneData);
  },

  updateZone: (id, zoneData) => {
    return ApiService.put(`/zones/${id}/`, zoneData);
  },

  deleteZone: (id) => {
    return ApiService.delete(`/zones/${id}/`);
  },

  // Real-time monitoring
  startMonitoring: (cameraId) => {
    return ApiService.post('/isg/monitoring/start/', { camera_id: cameraId });
  },

  stopMonitoring: (cameraId) => {
    return ApiService.post('/isg/monitoring/stop/', { camera_id: cameraId });
  },

  getMonitoringStatus: (cameraId) => {
    return ApiService.get(`/isg/monitoring/status/${cameraId}/`);
  },

  // Analytics and statistics
  getSafetyStats: (params = {}) => {
    return ApiService.get('/isg/statistics/', params);
  },

  getEquipmentComplianceRate: (startDate, endDate) => {
    return ApiService.get('/isg/compliance-rate/', {
      start_date: startDate,
      end_date: endDate
    });
  },

  getZoneViolationHeatmap: (zoneId, startDate, endDate) => {
    return ApiService.get(`/isg/zone-heatmap/${zoneId}/`, {
      start_date: startDate,
      end_date: endDate
    });
  }
};

export default ISGService;
