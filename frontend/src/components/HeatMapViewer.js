import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Select, DatePicker, Button, Card, Alert, Spin, Empty, Divider, Tabs, Table, Row, Col, Typography } from 'antd';
import { HeatMapOutlined, HistoryOutlined, AreaChartOutlined, EnvironmentOutlined } from '@ant-design/icons';
import './HeatMapViewer.css';

const { TabPane } = Tabs;
const { Option } = Select;
const { RangePicker } = DatePicker;
const { Title, Text } = Typography;

const HeatMapViewer = () => {
  // State tanımlamaları
  const [cameras, setCameras] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState(null);
  const [dateRange, setDateRange] = useState([null, null]);
  const [mapType, setMapType] = useState('daily');
  const [heatMapData, setHeatMapData] = useState(null);
  const [trackingData, setTrackingData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [heatMapUrl, setHeatMapUrl] = useState(null);
  const [currentTab, setCurrentTab] = useState('heatmap');

  // Kameraları yükle
  useEffect(() => {
    fetchCameras();
  }, []);

  // Kamera listesini sunucudan çekme
  const fetchCameras = async () => {
    try {
      const response = await axios.get('/api/cameras/');
      setCameras(response.data.results || response.data);
      if (response.data.results && response.data.results.length > 0) {
        setSelectedCamera(response.data.results[0].id);
      } else if (response.data && response.data.length > 0) {
        setSelectedCamera(response.data[0].id);
      }
    } catch (err) {
      console.error("Kameralar yüklenirken hata oluştu:", err);
      setError("Kamera listesi yüklenemedi: " + (err.response?.data?.detail || err.message));
    }
  };

  // Isı haritası verilerini getir
  const fetchHeatMap = async () => {
    if (!selectedCamera || !dateRange[0] || !dateRange[1]) {
      setError("Lütfen kamera ve tarih aralığı seçin");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const startDate = dateRange[0].format('YYYY-MM-DD');
      const endDate = dateRange[1].format('YYYY-MM-DD');

      const response = await axios.get(`/heatmap/`, {
        params: {
          camera_id: selectedCamera,
          start_date: startDate,
          end_date: endDate,
          map_type: mapType
        }
      });

      setHeatMapData(response.data);
      
      // Eğer ısı haritası görüntüsü varsa, URL'yi güncelle
      if (response.data && response.data.id) {
        setHeatMapUrl(`/heatmap/${response.data.id}/image/?timestamp=${new Date().getTime()}`);
      } else {
        setHeatMapUrl(null);
      }

      // Hareket verilerini de getir
      fetchTrackingData(startDate, endDate);
    } catch (err) {
      console.error("Isı haritası yüklenirken hata oluştu:", err);
      setError("Isı haritası oluşturulamadı: " + (err.response?.data?.detail || err.message));
      setHeatMapUrl(null);
    } finally {
      setLoading(false);
    }
  };

  // Hareket verilerini getir
  const fetchTrackingData = async (startDate, endDate) => {
    try {
      const response = await axios.get(`/tracking-data/`, {
        params: {
          camera_id: selectedCamera,
          start_date: startDate,
          end_date: endDate
        }
      });

      setTrackingData(response.data.results || response.data);
    } catch (err) {
      console.error("Hareket verileri yüklenirken hata oluştu:", err);
      // Ana hata mesajını değiştirmeden sadece konsola yazdırıyoruz
    }
  };

  // Yeni ısı haritası oluştur
  const generateNewHeatMap = async () => {
    if (!selectedCamera || !dateRange[0] || !dateRange[1]) {
      setError("Lütfen kamera ve tarih aralığı seçin");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const startDate = dateRange[0].format('YYYY-MM-DD');
      const endDate = dateRange[1].format('YYYY-MM-DD');

      const response = await axios.post(`/api/isg/heatmaps/generate_heatmap/`, {
        camera_id: selectedCamera,
        start_date: startDate,
        end_date: endDate,
        map_type: mapType
      });

      // Başarılı olursa, ısı haritasını yeniden getir
      if (response.data && response.data.heatmap_url) {
        // Kısa bir gecikme verip ardından ısı haritasını yükle
        setTimeout(() => {
          fetchHeatMap();
        }, 1000);
      }
    } catch (err) {
      console.error("Isı haritası oluşturma isteği gönderilirken hata oluştu:", err);
      setError("Isı haritası oluşturma isteği gönderilemedi: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Tarih aralığı değiştiğinde
  const handleDateRangeChange = (dates) => {
    setDateRange(dates);
  };

  // Kamera değiştiğinde
  const handleCameraChange = (value) => {
    setSelectedCamera(value);
  };

  // Harita tipi değiştiğinde
  const handleMapTypeChange = (value) => {
    setMapType(value);
  };

  // Tab değiştiğinde
  const handleTabChange = (key) => {
    setCurrentTab(key);
  };

  // Hareket verileri için tablo sütunları
  const trackingColumns = [
    {
      title: 'Kişi ID',
      dataIndex: 'person_id',
      key: 'person_id',
    },
    {
      title: 'X Konumu',
      dataIndex: 'position_x',
      key: 'position_x',
      render: (text) => Math.round(text),
    },
    {
      title: 'Y Konumu',
      dataIndex: 'position_y',
      key: 'position_y',
      render: (text) => Math.round(text),
    },
    {
      title: 'Baret Durumu',
      dataIndex: 'has_helmet',
      key: 'has_helmet',
      render: (text) => (text ? 'Var' : 'Yok'),
    },
    {
      title: 'Tarih',
      dataIndex: 'tracking_date',
      key: 'tracking_date',
    },
    {
      title: 'Zaman',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text) => new Date(text).toLocaleTimeString(),
    },
  ];

  return (
    <div className="heat-map-viewer">
      <Card title={<><HeatMapOutlined /> İşçi Hareket Haritası</>} className="control-card">
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <div className="form-item">
              <label>Kamera Seçin:</label>
              <Select
                placeholder="Kamera seçin"
                value={selectedCamera}
                onChange={handleCameraChange}
                style={{ width: '100%' }}
                loading={cameras.length === 0}
              >
                {cameras.map(camera => (
                  <Option key={camera.id} value={camera.id}>{camera.name || `Kamera ${camera.id}`}</Option>
                ))}
              </Select>
            </div>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <div className="form-item">
              <label>Tarih Aralığı:</label>
              <RangePicker
                style={{ width: '100%' }}
                value={dateRange}
                onChange={handleDateRangeChange}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} md={4}>
            <div className="form-item">
              <label>Harita Tipi:</label>
              <Select
                placeholder="Harita tipi"
                value={mapType}
                onChange={handleMapTypeChange}
                style={{ width: '100%' }}
              >
                <Option value="daily">Günlük</Option>
                <Option value="weekly">Haftalık</Option>
                <Option value="monthly">Aylık</Option>
              </Select>
            </div>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <div className="form-item button-container">
              <Button type="primary" onClick={fetchHeatMap} loading={loading}>
                Haritayı Görüntüle
              </Button>
              <Button onClick={generateNewHeatMap} loading={loading}>
                Yeni Oluştur
              </Button>
            </div>
          </Col>
        </Row>
      </Card>

      {error && (
        <Alert
          message="Hata"
          description={error}
          type="error"
          showIcon
          closable
          style={{ marginTop: 16 }}
        />
      )}

      <Tabs defaultActiveKey="heatmap" onChange={handleTabChange} style={{ marginTop: 16 }}>
        <TabPane
          tab={<span><HeatMapOutlined /> Isı Haritası</span>}
          key="heatmap"
        >
          <Card className="result-card">
            {loading ? (
              <div className="loading-container">
                <Spin size="large" />
                <p>Isı haritası oluşturuluyor...</p>
              </div>
            ) : heatMapUrl ? (
              <div className="heat-map-container">
                <img 
                  src={heatMapUrl} 
                  alt="İşçi Hareket Isı Haritası" 
                  className="heat-map-image" 
                />
                <div className="heat-map-info">
                  <Divider orientation="left">Isı Haritası Bilgileri</Divider>
                  <p><strong>Kamera:</strong> {cameras.find(c => c.id === selectedCamera)?.name || 'Bilinmeyen Kamera'}</p>
                  <p><strong>Başlangıç Tarihi:</strong> {heatMapData?.start_date}</p>
                  <p><strong>Bitiş Tarihi:</strong> {heatMapData?.end_date}</p>
                  <p><strong>Harita Tipi:</strong> {heatMapData?.map_type_display || mapType}</p>
                  <p><strong>Oluşturulma Zamanı:</strong> {heatMapData?.generated_at && new Date(heatMapData.generated_at).toLocaleString()}</p>
                </div>
              </div>
            ) : (
              <Empty
                description={
                  <span>
                    Henüz ısı haritası oluşturulmadı. Lütfen kamera ve tarih aralığı seçip "Haritayı Görüntüle" butonuna tıklayın.
                  </span>
                }
              />
            )}
          </Card>
        </TabPane>
        <TabPane
          tab={<span><HistoryOutlined /> Hareket Verileri</span>}
          key="tracking-data"
        >
          <Card className="result-card">
            {loading ? (
              <div className="loading-container">
                <Spin size="large" />
                <p>Veriler yükleniyor...</p>
              </div>
            ) : trackingData.length > 0 ? (
              <div className="tracking-data-container">
                <Table 
                  dataSource={trackingData} 
                  columns={trackingColumns} 
                  rowKey="id"
                  pagination={{ pageSize: 10 }}
                  scroll={{ x: 'max-content' }}
                />
              </div>
            ) : (
              <Empty
                description={
                  <span>
                    Seçilen tarih aralığında hareket verisi bulunamadı.
                  </span>
                }
              />
            )}
          </Card>
        </TabPane>
        <TabPane
          tab={<span><AreaChartOutlined /> Analiz</span>}
          key="analysis"
        >
          <Card className="result-card">
            <div className="analysis-container">
              <Title level={4}>Hareket Analizi</Title>
              
              <Row gutter={[16, 16]}>
                <Col xs={24} md={12}>
                  <Card title="Yoğunluk Özeti" bordered={false}>
                    {trackingData.length > 0 ? (
                      <>
                        <p><EnvironmentOutlined /> Toplam Kayıt Sayısı: <strong>{trackingData.length}</strong></p>
                        <p><EnvironmentOutlined /> Baretli Kişi Sayısı: <strong>
                          {trackingData.filter(item => item.has_helmet).length}
                        </strong></p>
                        <p><EnvironmentOutlined /> Baretsiz Kişi Sayısı: <strong>
                          {trackingData.filter(item => !item.has_helmet).length}
                        </strong></p>
                      </>
                    ) : (
                      <Empty description="Veri bulunamadı" />
                    )}
                  </Card>
                </Col>
                <Col xs={24} md={12}>
                  <Card title="Öneriler" bordered={false}>
                    {trackingData.length > 0 ? (
                      <>
                        <p>
                          <strong>Baret Kullanım Oranı: </strong> 
                          {Math.round((trackingData.filter(item => item.has_helmet).length / trackingData.length) * 100)}%
                        </p>
                        <Alert
                          message="İyileştirme Önerileri"
                          description="Hareket haritasında yoğunluk gözlenen bölgelerde iş akışı düzenlenebilir ve darboğazlar giderilebilir. Ayrıca, baret kullanım oranı düşük ise güvenlik eğitimleri ve denetimler artırılabilir."
                          type="info"
                          showIcon
                        />
                      </>
                    ) : (
                      <Empty description="Veri bulunamadı" />
                    )}
                  </Card>
                </Col>
              </Row>
            </div>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default HeatMapViewer;
