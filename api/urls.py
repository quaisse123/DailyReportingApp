from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import generate_report_pdf

router = DefaultRouter()

router.register(r'reports', views.DailyReportViewSet, basename='report')
router.register(r'report-contractors', views.ReportContractorViewSet, basename='reportContractants')
router.register(r'contractors', views.ContractorViewSet, basename='Contractants')
router.register(r'report-contractor-zones', views.ReportContractorZoneViewSet, basename='reportContractorZones')
router.register(r'zones', views.ZoneViewSet, basename='zones')
router.register(r'equipments', views.EquipmentViewSet, basename='equipments')
router.register(r'equipment-assignments', views.EquipmentAssignmentViewSet, basename='equipmentAssignments')
router.register(r'activities', views.ActivityViewSet, basename='activities')
router.register(r'activity-photos', views.PhotoViewSet, basename='activityPhotos')
urlpatterns = [
    path('', include(router.urls)),
    # path('activity-photos/upload/', views.ActivityPhotoUploadView.as_view(), name='activity-photo-upload'),
    path('reports/<int:report_id>/pdf/', generate_report_pdf, name='generate_report_pdf'),
]