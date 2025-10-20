from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from AuthApi.models import CustomUser
 
class DailyReport(models.Model):
    user = models.ForeignKey(CustomUser, related_name="daily_reports", on_delete=models.CASCADE)

    date = models.DateField()
    comments = models.TextField(blank=True)
    class Meta:
        unique_together = ('user', 'date')
    def __str__(self):
        return f"Rapport du {self.date}"

class Contractor(models.Model):
    user = models.ForeignKey(CustomUser, related_name="contractors", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='contractors_logos/', blank=True, null=True)
    thumbnail = ImageSpecField(
        source='logo',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 70}
    )
    def __str__(self):
        return self.name

class Zone(models.Model):
    user = models.ForeignKey(CustomUser, related_name="zones", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    access = models.BooleanField(default=True)
    def __str__(self):
        return self.name
   
# Lien entre un rapport et un contractor, sans zone obligatoire
class ReportContractor(models.Model):
    daily_report = models.ForeignKey(DailyReport, related_name="report_contractors", on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, related_name="report_contractors", on_delete=models.CASCADE)
 
    class Meta:
        unique_together = ('daily_report', 'contractor')

    def __str__(self):
        return f"{self.daily_report.date} - {self.contractor.name}"

# Lien entre un ReportContractor et une zone (possibilité d’avoir plusieurs zones par contractor dans un rapport)
class ReportContractorZone(models.Model):
    report_contractor = models.ForeignKey(ReportContractor, related_name="zones", on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, related_name="report_contractor_zones", on_delete=models.CASCADE)

    # class Meta:
    #     unique_together = ('report_contractor', 'zone')

    def __str__(self):
        return f"{self.report_contractor} - {self.zone.name}"

class Equipment(models.Model):
    user = models.ForeignKey(CustomUser, related_name="equipements", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    availability = models.BooleanField(default=True)
    def __str__(self):
        return self.name
 
# Equipements affectés à un report/contractor/zone
class EquipmentAssignment(models.Model):
    report_contractor_zone = models.ForeignKey(ReportContractorZone, related_name="equipment_assignments", on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, related_name="assignments", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"ID : {self.id} - {self.report_contractor_zone} - {self.equipment.name} ({self.quantity})"

# Activités liées à un report/contractor/zone
class Activity(models.Model):
    report_contractor_zone = models.ForeignKey(ReportContractorZone, related_name="activities", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.report_contractor_zone})"



class Photo(models.Model):
    activity = models.ForeignKey(Activity, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='activity_photos/')
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 70}
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.activity.name} on {self.timestamp}"
