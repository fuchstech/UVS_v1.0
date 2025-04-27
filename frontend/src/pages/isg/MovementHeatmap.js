import React from 'react';
import { PageHeader } from 'antd';
import HeatMapViewer from '../../components/HeatMapViewer';

const MovementHeatmap = () => {
  return (
    <div className="movement-heatmap-page">
      <PageHeader
        title="İşçi Hareket Haritası"
        subTitle="İşçilerin hareketlerini izleyerek yoğunluk haritasını görüntüleyin"
        className="site-page-header"
      />
      
      <div className="page-content">
        <HeatMapViewer />
      </div>
    </div>
  );
};

export default MovementHeatmap;
