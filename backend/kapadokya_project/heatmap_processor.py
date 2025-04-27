"""
İşçilerin hareket verilerini işleyerek ısı haritası oluşturan modül
"""
import os
import cv2
import numpy as np
import json
import datetime
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .isg.models import PersonTrackingData, HeatMap
from .isg.serializers import HeatMapSerializer
from .api.models import Camera


class HeatMapProcessor:
    """
    İşçi hareket verilerini işleyerek ısı haritası oluşturan sınıf
    """
    def __init__(self, camera_id=None, resolution=(640, 480)):
        self.camera_id = camera_id
        self.width, self.height = resolution
        self.heat_map = np.zeros((self.height, self.width), dtype=np.float32)
    
    def add_point(self, x, y, intensity=1.0):
        """
        Isı haritasına nokta ekler
        """
        # Koordinatların görüntü sınırları içinde olduğundan emin ol
        if 0 <= x < self.width and 0 <= y < self.height:
            # Gaussian dağılım ile noktayı ekle
            sigma = 20  # Gaussian dağılımın standart sapması
            for i in range(max(0, int(y) - 3 * sigma), min(self.height, int(y) + 3 * sigma)):
                for j in range(max(0, int(x) - 3 * sigma), min(self.width, int(x) + 3 * sigma)):
                    # Merkez noktadan uzaklık
                    dist = np.sqrt((i - y) ** 2 + (j - x) ** 2)
                    # Gaussian dağılım ile ağırlık hesapla
                    weight = np.exp(-(dist ** 2) / (2 * sigma ** 2)) * intensity
                    # Isı haritasına ekle
                    self.heat_map[i, j] += weight
    
    def add_tracking_data(self, tracking_data):
        """
        Veritabanındaki izleme verilerini ısı haritasına ekler
        """
        for data in tracking_data:
            self.add_point(data.position_x, data.position_y, 1.0)
    
    def generate_heat_map_image(self, background_image=None):
        """
        Isı haritası görüntüsü oluşturur
        """
        # Isı haritasını normalize et
        if np.max(self.heat_map) > 0:
            norm_heat_map = self.heat_map / np.max(self.heat_map)
        else:
            norm_heat_map = self.heat_map
        
        # Isı haritasını 8-bit formata dönüştür
        norm_heat_map = (norm_heat_map * 255).astype(np.uint8)
        
        # Jet renk haritası uygula
        colored_map = cv2.applyColorMap(norm_heat_map, cv2.COLORMAP_JET)
        
        if background_image is not None:
            # Arka plan görüntüsünü ısı haritası boyutuna yeniden boyutlandır
            bg = cv2.resize(background_image, (self.width, self.height))
            # Isı haritası ve arka planı karıştır
            alpha = 0.7  # Opaklık
            result = cv2.addWeighted(colored_map, alpha, bg, 1 - alpha, 0)
            return result
        else:
            return colored_map
    
    def save_heat_map(self, camera, start_date, end_date, map_type='daily'):
        """
        Isı haritasını veritabanına kaydeder
        """
        # Görüntüyü oluştur
        heat_map_image = self.generate_heat_map_image()
        
        # Görüntüyü dosya olarak kaydet
        filename = f"heatmap_{camera.id}_{start_date.strftime('%Y%m%d')}_{map_type}.jpg"
        image_path = os.path.join('heatmaps', filename)
        
        # Görüntüyü JPEG formatına dönüştür
        _, buffer = cv2.imencode('.jpg', heat_map_image)
        image_file = ContentFile(buffer.tobytes())
        
        # Dosyayı media klasörüne kaydet
        saved_path = default_storage.save(image_path, image_file)
        
        # Isı haritası verisini JSON formatında hazırla
        heat_map_data = {
            'points': self.heat_map.tolist(),  # NumPy dizisini list'e dönüştür
            'max_value': float(np.max(self.heat_map)),
            'image_path': saved_path,
            'resolution': {'width': self.width, 'height': self.height}
        }
        
        # Veritabanına kaydet
        heat_map_obj, created = HeatMap.objects.update_or_create(
            camera=camera,
            start_date=start_date,
            end_date=end_date,
            map_type=map_type,
            defaults={'heat_map_data': heat_map_data}
        )
        
        return heat_map_obj


@method_decorator(csrf_exempt, name='dispatch')
class HeatMapGeneratorView(APIView):
    """
    Isı haritası oluşturan ve döndüren API
    """
    def get(self, request):
        """
        Belirli bir kamera ve tarih aralığı için ısı haritası döndürür
        """
        try:
            camera_id = request.query_params.get('camera_id')
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            map_type = request.query_params.get('map_type', 'daily')
            
            if not camera_id:
                return Response({"error": "Kamera ID'si gerekli"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                camera = Camera.objects.get(id=camera_id)
            except Camera.DoesNotExist:
                return Response({"error": "Kamera bulunamadı"}, status=status.HTTP_404_NOT_FOUND)
            
            # Tarih formatını ayarla
            today = timezone.now().date()
            
            if start_date_str:
                try:
                    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response({"error": "Geçersiz başlangıç tarihi formatı. YYYY-MM-DD kullanın"}, 
                                   status=status.HTTP_400_BAD_REQUEST)
            else:
                # Varsayılan olarak bugün
                start_date = today
            
            if end_date_str:
                try:
                    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response({"error": "Geçersiz bitiş tarihi formatı. YYYY-MM-DD kullanın"}, 
                                   status=status.HTTP_400_BAD_REQUEST)
            else:
                # Varsayılan olarak bugün
                end_date = today
            
            # Veritabanında kayıtlı ısı haritasını kontrol et
            try:
                heat_map = HeatMap.objects.get(
                    camera=camera,
                    start_date=start_date,
                    end_date=end_date,
                    map_type=map_type
                )
                # Kayıtlı ısı haritasını döndür
                serializer = HeatMapSerializer(heat_map)
                return Response(serializer.data)
            except HeatMap.DoesNotExist:
                # Yeni ısı haritası oluştur
                pass
            
            # Tarih aralığındaki izleme verilerini al
            tracking_data = PersonTrackingData.objects.filter(
                camera=camera,
                tracking_date__gte=start_date,
                tracking_date__lte=end_date
            )
            
            if not tracking_data.exists():
                return Response({"error": "Belirtilen tarih aralığında veri bulunamadı"}, 
                               status=status.HTTP_404_NOT_FOUND)
            
            # Kamera çözünürlüğünü belirle
            resolution = (640, 480)  # Varsayılan çözünürlük
            
            # Isı haritası işlemcisini oluştur
            processor = HeatMapProcessor(camera.id, resolution)
            
            # İzleme verilerini ekle
            processor.add_tracking_data(tracking_data)
            
            # Isı haritasını kaydet ve döndür
            heat_map = processor.save_heat_map(camera, start_date, end_date, map_type)
            serializer = HeatMapSerializer(heat_map)
            
            return Response(serializer.data)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class HeatMapImageView(APIView):
    """
    Isı haritası görüntüsünü döndüren API
    """
    def get(self, request, heat_map_id):
        """
        Belirli bir ısı haritasının görüntüsünü döndürür
        """
        try:
            heat_map = HeatMap.objects.get(id=heat_map_id)
            heat_map_data = heat_map.get_data()
            
            if 'image_path' not in heat_map_data:
                return Response({"error": "Isı haritası görüntüsü bulunamadı"}, 
                               status=status.HTTP_404_NOT_FOUND)
            
            # Görüntüyü dosyadan oku
            image_path = os.path.join(settings.MEDIA_ROOT, heat_map_data['image_path'])
            
            if not os.path.exists(image_path):
                return Response({"error": "Isı haritası görüntü dosyası bulunamadı"}, 
                               status=status.HTTP_404_NOT_FOUND)
            
            # Görüntüyü oku ve döndür
            with open(image_path, 'rb') as f:
                return HttpResponse(f.read(), content_type='image/jpeg')
            
        except HeatMap.DoesNotExist:
            return Response({"error": "Isı haritası bulunamadı"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class TrackingDataAPIView(APIView):
    """
    İşçi izleme verilerini yönetme API'si
    """
    def post(self, request):
        """
        Yeni izleme verisi ekler
        """
        try:
            camera_id = request.data.get('camera_id')
            position_x = request.data.get('position_x')
            position_y = request.data.get('position_y')
            person_id = request.data.get('person_id')
            has_helmet = request.data.get('has_helmet', False)
            confidence = request.data.get('confidence', 0.0)
            
            if not all([camera_id, position_x is not None, position_y is not None]):
                return Response({"error": "Kamera ID, X ve Y pozisyonları gerekli"}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            try:
                camera = Camera.objects.get(id=camera_id)
            except Camera.DoesNotExist:
                return Response({"error": "Kamera bulunamadı"}, status=status.HTTP_404_NOT_FOUND)
            
            # Yeni izleme verisi oluştur
            tracking_data = PersonTrackingData.objects.create(
                camera=camera,
                tracking_date=timezone.now().date(),
                position_x=float(position_x),
                position_y=float(position_y),
                person_id=person_id,
                has_helmet=has_helmet,
                confidence=float(confidence),
                frame_number=request.data.get('frame_number', 0)
            )
            
            # Serilize edip döndür
            from .isg.serializers import PersonTrackingDataSerializer
            serializer = PersonTrackingDataSerializer(tracking_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """
        İzleme verilerini listeler
        """
        try:
            camera_id = request.query_params.get('camera_id')
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            
            queryset = PersonTrackingData.objects.all()
            
            if camera_id:
                queryset = queryset.filter(camera_id=camera_id)
            
            if start_date_str:
                try:
                    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    queryset = queryset.filter(tracking_date__gte=start_date)
                except ValueError:
                    return Response({"error": "Geçersiz başlangıç tarihi formatı. YYYY-MM-DD kullanın"}, 
                                   status=status.HTTP_400_BAD_REQUEST)
            
            if end_date_str:
                try:
                    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    queryset = queryset.filter(tracking_date__lte=end_date)
                except ValueError:
                    return Response({"error": "Geçersiz bitiş tarihi formatı. YYYY-MM-DD kullanın"}, 
                                   status=status.HTTP_400_BAD_REQUEST)
            
            # Sayfalama
            from rest_framework.pagination import PageNumberPagination
            paginator = PageNumberPagination()
            paginator.page_size = 50  # Her sayfada 50 veri
            result_page = paginator.paginate_queryset(queryset, request)
            
            # Serilize et
            from .isg.serializers import PersonTrackingDataSerializer
            serializer = PersonTrackingDataSerializer(result_page, many=True)
            
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
