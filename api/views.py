from rest_framework import viewsets
from .models import DailyReport, ReportContractorZone
from .serializers import DailyReportSerializer, ReportContractorZoneSerializer
from .models import Contractor
from .serializers import ContractorSerializer
from .models import ReportContractor
from .serializers import ReportContractorSerializer
from .models import Zone
from .serializers import ZoneSerializer
from .models import Equipment
from .serializers import EquipmentSerializer
from .models import EquipmentAssignment
from .serializers import EquipmentAssignmentSerializer
from .models import Activity
from .serializers import ActivitySerializer
from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Photo, Activity
from .serializers import PhotoSerializer

class DailyReportViewSet(viewsets.ModelViewSet):
    queryset = DailyReport.objects.all().order_by('-date')
    serializer_class = DailyReportSerializer

    # à chaque création on associe le rapport au suer connecté
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                {"error": "Un rapport existe déjà pour cette date."},
                status=status.HTTP_400_BAD_REQUEST
            )
    # Pour le GET , retourne juste les rapport du user connecté
    def get_queryset(self):
        return DailyReport.objects.filter(user=self.request.user).order_by('-date')

class ContractorViewSet(viewsets.ModelViewSet):
    queryset = Contractor.objects.all()
    serializer_class = ContractorSerializer

    # à chaque création on associe le rapport au suer connecté
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    # Pour le GET , retourne juste les rapport du user connecté
    def get_queryset(self):
        return Contractor.objects.filter(user=self.request.user)

class ReportContractorViewSet(viewsets.ModelViewSet):
    queryset = ReportContractor.objects.all()
    serializer_class = ReportContractorSerializer

    def get_queryset(self):
        return ReportContractor.objects.filter(daily_report__user=self.request.user)

class ReportContractorZoneViewSet(viewsets.ModelViewSet):
    queryset = ReportContractorZone.objects.all()
    serializer_class = ReportContractorZoneSerializer
    
    def get_queryset(self):
        return ReportContractorZone.objects.filter(report_contractor__daily_report__user=self.request.user)

class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all().order_by('name')
    serializer_class = ZoneSerializer

    # à chaque création on associe le rapport au suer connecté
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    # Pour le GET , retourne juste les rapport du user connecté
    def get_queryset(self):
        return Zone.objects.filter(user=self.request.user)

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all().order_by('name')
    serializer_class = EquipmentSerializer

    # à chaque création on associe le rapport au suer connecté
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    # Pour le GET , retourne juste les rapport du user connecté
    def get_queryset(self):
        return Equipment.objects.filter(user=self.request.user)

class EquipmentAssignmentViewSet(viewsets.ModelViewSet):
    queryset = EquipmentAssignment.objects.all()
    serializer_class = EquipmentAssignmentSerializer
    filterset_fields = ['equipment', 'report_contractor_zone']

    def get_queryset(self):
        # Start with base queryset filtered by user
        base_queryset = EquipmentAssignment.objects.filter(
            equipment__user=self.request.user
        )
        
        # Get filter parameters from request
        equipment_id = self.request.query_params.get('equipment')
        zone_id = self.request.query_params.get('report_contractor_zone')
        
        # Apply additional filters if provided
        if equipment_id:
            base_queryset = base_queryset.filter(equipment_id=equipment_id)
        if zone_id:
            base_queryset = base_queryset.filter(report_contractor_zone_id=zone_id)
        
        return base_queryset

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    filterset_fields = ['report_contractor_zone']

    # Ajout d'un filtre custom pour contractor
    def get_queryset(self):
        queryset = Activity.objects.filter(report_contractor_zone__report_contractor__daily_report__user=self.request.user)
        contractor_id = self.request.query_params.get('contractor')
        if contractor_id:
            queryset = queryset.filter(report_contractor_zone__report_contractor__contractor_id=contractor_id)
        return queryset

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def create(self, request, *args, **kwargs):
        activity_id = request.data.get('activity')
        images = request.FILES.getlist('image')  # Récupère tous les fichiers envoyés sous 'image'
        if not activity_id or not images:
            return Response({'error': 'activity and image(s) required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            activity = Activity.objects.get(id=activity_id)
            photos = []
            for image in images:
                photo = Photo.objects.create(activity=activity, image=image)
                photos.append(photo)
            serializer = PhotoSerializer(photos, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Activity.DoesNotExist:
            return Response({'error': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)
    def get_queryset(self):
        return Photo.objects.filter(activity__report_contractor_zone__report_contractor__daily_report__user=self.request.user)
    

from django.template.loader import render_to_string  # Pour rendre un template HTML en chaîne de caractères
from django.http import HttpResponse  # Pour retourner une réponse HTTP personnalisée
from weasyprint import HTML  # Pour convertir du HTML en PDF
from .models import DailyReport  # Import du modèle DailyReport

from rest_framework.decorators import api_view, permission_classes  # Pour créer une vue API basée sur une fonction
from rest_framework.permissions import IsAuthenticated  # Pour restreindre l'accès aux utilisateurs authentifiés

@api_view(['GET'])  # Déclare que cette vue accepte uniquement les requêtes GET
@permission_classes([IsAuthenticated])  # Restreint l'accès à la vue aux utilisateurs connectés
def generate_report_pdf(request, report_id):
    # Récupère le rapport avec toutes les relations nécessaires pour éviter les requêtes supplémentaires
    report = DailyReport.objects.prefetch_related(
        'report_contractors__contractor',  # Précharge les contractants liés au rapport
        'report_contractors__zones__zone',  # Précharge les zones liées aux contractants du rapport
        'report_contractors__zones__equipment_assignments__equipment',  # Précharge les équipements assignés dans chaque zone
        'report_contractors__zones__activities__photos'  # Précharge les photos des activités dans chaque zone
    ).get(id=report_id, user=request.user)  # Filtre sur l'id du rapport et l'utilisateur connecté

    # Prépare le contexte à passer au template HTML
    context = {'report': report}
    # Rend le template HTML en chaîne de caractères avec le contexte
    html_string = render_to_string('api/report_pdf.html', context)
    # Génère le PDF à partir du HTML rendu
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    # Crée une réponse HTTP avec le PDF comme contenu
    response = HttpResponse(pdf_file, content_type='application/pdf')
    # Définit le nom du fichier PDF à télécharger
    response['Content-Disposition'] = f'attachment; filename="rapport_{report.date}.pdf"'
    # Retourne la réponse HTTP contenant le PDF
    return response