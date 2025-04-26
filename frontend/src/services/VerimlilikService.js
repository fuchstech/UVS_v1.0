import ApiService from './ApiService';

const VerimlilikService = {
  // Worker management
  getWorkers: (params = {}) => {
    return ApiService.get('/verim/workers/', params);
  },

  getWorkerById: (id) => {
    return ApiService.get(`/verim/workers/${id}/`);
  },

  createWorker: (workerData) => {
    return ApiService.post('/verim/workers/', workerData);
  },

  updateWorker: (id, workerData) => {
    return ApiService.put(`/verim/workers/${id}/`, workerData);
  },

  deleteWorker: (id) => {
    return ApiService.delete(`/verim/workers/${id}/`);
  },

  // Work area management
  getWorkAreas: () => {
    return ApiService.get('/verim/work-areas/');
  },

  getWorkAreaById: (id) => {
    return ApiService.get(`/verim/work-areas/${id}/`);
  },

  createWorkArea: (workAreaData) => {
    return ApiService.post('/verim/work-areas/', workAreaData);
  },

  updateWorkArea: (id, workAreaData) => {
    return ApiService.put(`/verim/work-areas/${id}/`, workAreaData);
  },

  deleteWorkArea: (id) => {
    return ApiService.delete(`/verim/work-areas/${id}/`);
  },

  // Worker activities
  getWorkerActivities: (params = {}) => {
    return ApiService.get('/verim/activities/', params);
  },

  // Productivity metrics
  getProductivityMetrics: () => {
    return ApiService.get('/verim/metrics/');
  },

  // Productivity data
  getProductivityData: (params = {}) => {
    return ApiService.get('/verim/productivity/', params);
  },

  getWorkerProductivity: (workerId, startDate, endDate) => {
    return ApiService.get(`/verim/productivity/`, {
      worker: workerId,
      start_date: startDate,
      end_date: endDate
    });
  },

  // Image processing for productivity
  processProductivityImage: (cameraId, workAreaId, imageFile, onProgress) => {
    const formData = new FormData();
    formData.append('camera_id', cameraId);
    formData.append('work_area_id', workAreaId);
    formData.append('image', imageFile);

    return ApiService.uploadFile('/verim/process-productivity/', formData, onProgress);
  },

  // Product management
  getProducts: () => {
    return ApiService.get('/verim/products/');
  },

  getProductById: (id) => {
    return ApiService.get(`/verim/products/${id}/`);
  },

  createProduct: (productData) => {
    return ApiService.post('/verim/products/', productData);
  },

  updateProduct: (id, productData) => {
    return ApiService.put(`/verim/products/${id}/`, productData);
  },

  deleteProduct: (id) => {
    return ApiService.delete(`/verim/products/${id}/`);
  },

  // Product count image processing
  processProductCountImage: (cameraId, productId, imageFile, onProgress) => {
    const formData = new FormData();
    formData.append('camera_id', cameraId);
    formData.append('product_id', productId);
    formData.append('image', imageFile);

    return ApiService.uploadFile('/verim/process-product-count/', formData, onProgress);
  },

  // Production counts
  getProductionCounts: (params = {}) => {
    return ApiService.get('/verim/production-counts/', params);
  },

  // Worker movement heatmap
  getWorkerHeatmap: (workAreaId, startDate, endDate) => {
    return ApiService.get(`/verim/worker-heatmap/${workAreaId}/`, {
      start_date: startDate,
      end_date: endDate
    });
  },

  // Worker identification
  identifyWorker: (imageFile) => {
    const formData = new FormData();
    formData.append('image', imageFile);

    return ApiService.uploadFile('/verim/identify-worker/', formData);
  },

  // Real-time monitoring
  startProductivityMonitoring: (cameraId, workAreaId) => {
    return ApiService.post('/verim/monitoring/start/', {
      camera_id: cameraId,
      work_area_id: workAreaId
    });
  },

  stopProductivityMonitoring: (cameraId) => {
    return ApiService.post('/verim/monitoring/stop/', {
      camera_id: cameraId
    });
  },

  // Analytics
  getProductivityStatistics: (workAreaId, startDate, endDate) => {
    return ApiService.get('/verim/statistics/', {
      work_area: workAreaId,
      start_date: startDate,
      end_date: endDate
    });
  },

  getWorkerComparison: (workAreaId, date) => {
    return ApiService.get('/verim/worker-comparison/', {
      work_area: workAreaId,
      date: date
    });
  },

  // Daily productivity report generation
  generateDailyReport: () => {
    return ApiService.post('/verim/generate-daily-report/');
  }
};

export default VerimlilikService;
