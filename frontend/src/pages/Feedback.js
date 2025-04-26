import React, { useState } from 'react';
import ApiService from '../services/ApiService';

const Feedback = () => {
  const [feedbackType, setFeedbackType] = useState('issue');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      await ApiService.post('/api/feedback/', {
        feedback_type: feedbackType,
        title,
        description
      });
      
      setSuccess(true);
      setTitle('');
      setDescription('');
      setFeedbackType('issue');
    } catch (error) {
      console.error('Error submitting feedback:', error);
      setError('Geri bildirim gönderilirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="feedback-container">
      <h2>Geri Bildirim</h2>
      
      {success && (
        <div className="success-message">
          Geri bildiriminiz başarıyla gönderildi. Teşekkür ederiz!
        </div>
      )}
      
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit} className="feedback-form">
        <div className="form-group">
          <label htmlFor="feedbackType">Geri Bildirim Türü</label>
          <select
            id="feedbackType"
            value={feedbackType}
            onChange={(e) => setFeedbackType(e.target.value)}
            required
          >
            <option value="issue">Sorun Bildirimi</option>
            <option value="suggestion">Öneri</option>
            <option value="improvement">İyileştirme</option>
            <option value="other">Diğer</option>
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="title">Başlık</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="description">Açıklama</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows="5"
            required
          ></textarea>
        </div>
        
        <button type="submit" disabled={loading} className="submit-button">
          {loading ? 'Gönderiliyor...' : 'Gönder'}
        </button>
      </form>
    </div>
  );
};

export default Feedback;