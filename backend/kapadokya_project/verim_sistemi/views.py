from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import (
    Worker, WorkArea, ProductivityMetric, WorkerActivity, 
    ProductivityData, Product, ProductionCount
)
from .serializers import (
    WorkerSerializer, WorkAreaSerializer, ProductivityMetricSerializer,
    WorkerActivitySerializer, ProductivityDataSerializer,
    ProductSerializer, ProductionCountSerializer
)
from .tasks import (
    process_productivity_image_task, process_product_count_task,
    generate_daily_productivity_report
)
from kapadokya_project.api.models import Camera, ProcessedImage

class WorkerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for worker management
    """
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Worker.objects.all()
        
        # Filter by active status
        is_active = self.request.query_params.get('active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
            
        # Filter by department
        department = self.request.query_params.get('department', None)
        if department:
            queryset = queryset.filter(department=department)
            
        return queryset

class WorkAreaViewSet(viewsets.ModelViewSet):
    """
    API endpoint for work area management
    """
    queryset = WorkArea.objects.all()
    serializer_class = WorkAreaSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductivityMetricViewSet(viewsets.ModelViewSet):
    """
    API endpoint for productivity metrics
    """
    queryset = ProductivityMetric.objects.all()
    serializer_class = ProductivityMetricSerializer
    permission_classes = [permissions.IsAuthenticated]

class WorkerActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for worker activities
    """
    queryset = WorkerActivity.objects.all().order_by('-timestamp')
    serializer_class = WorkerActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = WorkerActivity.objects.all().order_by('-timestamp')
        
        # Filter by worker
        worker_id = self.request.query_params.get('worker', None)
        if worker_id:
            queryset = queryset.filter(worker_id=worker_id)
            
        # Filter by work area
        work_area_id = self.request.query_params.get('work_area', None)
        if work_area_id:
            queryset = queryset.filter(work_area_id=work_area_id)
            
        # Filter by activity type
        activity_type = self.request.query_params.get('activity_type', None)
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(timestamp__date__range=[start_date, end_date])
            
        return queryset

class ProductivityDataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for productivity data
    """
    queryset = ProductivityData.objects.all()
    serializer_class = ProductivityDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ProductivityData.objects.all()
        
        # Filter by worker
        worker_id = self.request.query_params.get('worker', None)
        if worker_id:
            queryset = queryset.filter(worker_id=worker_id)
            
        # Filter by work area
        work_area_id = self.request.query_params.get('work_area', None)
        if work_area_id:
            queryset = queryset.filter(work_area_id=work_area_id)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
            
        # Filter by minimum productivity score
        min_score = self.request.query_params.get('min_score', None)
        if min_score:
            queryset = queryset.filter(productivity_score__gte=float(min_score))
            
        return queryset

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for product management
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductionCountViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for production count data
    """
    queryset = ProductionCount.objects.all()
    serializer_class = ProductionCountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ProductionCount.objects.all()
        
        # Filter by product
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
            
        # Filter by camera
        camera_id = self.request.query_params.get('camera', None)
        if camera_id:
            queryset = queryset.filter(camera_id=camera_id)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
            
        return queryset

class ProcessProductivityAPIView(APIView):
    """
    API endpoint to process images for worker productivity
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        # Get camera ID from request
        camera_id = request.data.get('camera_id')
        if not camera_id:
            return Response(
                {"detail": "Kamera ID'si gerekli."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get work area ID from request
        work_area_id = request.data.get('work_area_id')
        if not work_area_id:
            return Response(
                {"detail": "Çalışma alanı ID'si gerekli."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            camera = Camera.objects.get(id=camera_id)
            work_area = WorkArea.objects.get(id=work_area_id)
        except (Camera.DoesNotExist, WorkArea.DoesNotExist):
            return Response(
                {"detail": "Kamera veya çalışma alanı bulunamadı."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Handle image upload
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {"detail": "Görüntü dosyası gerekli."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save the original image
        processed_image = ProcessedImage.objects.create(
            camera=camera,
            original_image=image_file,
            detection_results={},  # Empty results, will be updated by task
        )
        
        # Process image in background
        process_productivity_image_task.delay(processed_image.id, work_area.id)
        
        return Response({
            "id": processed_image.id,
            "status": "Görüntü işleme kuyruğa alındı.",
            "message": "İşçi verimliliği analizi yapılıyor, sonuçlar yakında hazır olacak."
        })

class ProcessProductCountAPIView(APIView):
    """
    API endpoint to process images for product counting
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        # Get camera ID from request
        camera_id = request.data.get('camera_id')
        if not camera_id:
            return Response(
                {"detail": "Kamera ID'si gerekli."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get product ID from request
        product_id = request.data.get('product_id')
        if not product_id:
            return Response(
                {"detail": "Ürün ID'si gerekli."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            camera = Camera.objects.get(id=camera_id)
            product = Product.objects.get(id=product_id)
        except (Camera.DoesNotExist, Product.DoesNotExist):
            return Response(
                {"detail": "Kamera veya ürün bulunamadı."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Handle image upload
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {"detail": "Görüntü dosyası gerekli."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save the original image
        processed_image = ProcessedImage.objects.create(
            camera=camera,
            original_image=image_file,
            detection_results={},  # Empty results, will be updated by task
        )
        
        # Process image in background
        process_product_count_task.delay(processed_image.id, product.id)
        
        return Response({
            "id": processed_image.id,
            "status": "Görüntü işleme kuyruğa alındı.",
            "message": "Ürün sayımı yapılıyor, sonuçlar yakında hazır olacak."
        })
