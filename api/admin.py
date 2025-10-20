from django.contrib import admin
from . import models

admin.site.register(models.Activity)
admin.site.register(models.DailyReport)
admin.site.register(models.Contractor)
admin.site.register(models.Zone)
admin.site.register(models.Equipment)
admin.site.register(models.Photo)
admin.site.register(models.ReportContractor)
admin.site.register(models.ReportContractorZone)
admin.site.register(models.EquipmentAssignment)