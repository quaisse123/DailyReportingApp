from rest_framework import serializers
from .models import (
    DailyReport, Contractor, Zone, ReportContractor,
    ReportContractorZone, Equipment, EquipmentAssignment,
    Activity, Photo
)

class PhotoSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(read_only=True)  # <-- Ajoute ce champ

    class Meta:
        model = Photo
        fields = '__all__'  # <-- Tu peux garder '__all__'
        
class ActivitySerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Activity
        fields = '__all__'


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'
        read_only_fields = ['user']


class EquipmentAssignmentSerializer(serializers.ModelSerializer):
    equipment_id = serializers.PrimaryKeyRelatedField(
        source='equipment',
        queryset=Equipment.objects.all(),
        write_only=True
    )
    equipment = EquipmentSerializer(read_only=True)

    class Meta:
        model = EquipmentAssignment
        fields = '__all__'


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'
        read_only_fields = ['user']


class ReportContractorZoneSerializer(serializers.ModelSerializer):
    # Champs pour GET (lecture seule)
    zone = ZoneSerializer(read_only=True)
    equipment_assignments = EquipmentAssignmentSerializer(many=True, read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)
    # Champs pour POST (écriture seule) : on reçoit juste les IDs
    report_contractor_id = serializers.PrimaryKeyRelatedField(
        source='report_contractor',
        queryset=ReportContractor.objects.all(),
        write_only=True,
    )
    zone_id = serializers.PrimaryKeyRelatedField(
        source='zone',
        queryset=Zone.objects.all(),
        write_only=True,
    )

    class Meta:
        model = ReportContractorZone
        fields = [
            'id',
            'report_contractor_id',
            'zone_id',
            'zone',
            'equipment_assignments',
            'activities',
        ]


class ContractorSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(read_only=True) 
    
    class Meta:
        model = Contractor
        fields = '__all__'
        read_only_fields = ['user']


class ReportContractorSerializer(serializers.ModelSerializer):
    # Champs pour GET (lecture seule)
    contractor = ContractorSerializer(read_only=True)
    zones = ReportContractorZoneSerializer(many=True, read_only=True)

    # Champs pour POST (écriture seule) : on reçoit juste les IDs
    daily_report_id = serializers.PrimaryKeyRelatedField(
        source='daily_report',
        queryset=DailyReport.objects.all(),
        write_only=True,
    )
    contractor_id = serializers.PrimaryKeyRelatedField(
        source='contractor',
        queryset=Contractor.objects.all(),
        write_only=True,
    )
    

    class Meta:
        model = ReportContractor
        fields = [
            'id',
            'daily_report_id',
            'contractor_id',
            'contractor',
            'zones',
        ]
    


class DailyReportSerializer(serializers.ModelSerializer):
    report_contractors = ReportContractorSerializer(many=True, read_only=True)

    class Meta:
        model = DailyReport
        fields = '__all__'
        read_only_fields = ['user']
