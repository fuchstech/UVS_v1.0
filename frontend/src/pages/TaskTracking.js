import React, { useState, useEffect } from 'react';
import ApiService from '../services/ApiService';

const TaskTracking = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        // Gerçek API yerine simüle edilmiş verileri kullanalım
        // const response = await ApiService.get('/api/verim/tasks/');
        const response = { data: ApiService.getSimulatedTasks() };
        setTasks(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching tasks:', error);
        setError('Görevler yüklenirken bir hata oluştu.');
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  if (loading) {
    return <div className="loading">Görevler yükleniyor...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="task-tracking">
      <h2>Görev Takibi</h2>
      
      <div className="task-filters">
        <select>
          <option value="all">Tüm Görevler</option>
          <option value="pending">Bekleyen</option>
          <option value="in-progress">Devam Eden</option>
          <option value="completed">Tamamlanan</option>
        </select>
        
        <input type="text" placeholder="Görev ara..." />
        
        <button className="add-task-btn">Yeni Görev</button>
      </div>
      
      <div className="tasks-list">
        {tasks.length === 0 ? (
          <p>Hiç görev bulunamadı.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Görev</th>
                <th>Sorumlu</th>
                <th>Durum</th>
                <th>Başlangıç</th>
                <th>Bitiş</th>
                <th>İşlemler</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.id}>
                  <td>{task.title}</td>
                  <td>{task.assigned_to}</td>
                  <td>
                    <span className={`status status-${task.status.toLowerCase()}`}>
                      {task.status}
                    </span>
                  </td>
                  <td>{new Date(task.start_date).toLocaleDateString()}</td>
                  <td>{task.end_date ? new Date(task.end_date).toLocaleDateString() : '-'}</td>
                  <td>
                    <button>Düzenle</button>
                    <button>Detay</button>
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

export default TaskTracking;