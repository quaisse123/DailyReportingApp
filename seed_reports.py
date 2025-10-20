# -*- coding: utf-8 -*-
# filepath: c:\Users\marou\Desktop\DailyReporting\backend\backend\seed_reports.py
# Pour exécuter ce script correctement avec les accents sous Windows:
# 1. Ouvrez une console CMD
# 2. Tapez: chcp 65001
# 3. Lancez le shell Django: python manage.py shell
# 4. Exécutez le script

from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import date, timedelta
from AuthApi.models import CustomUser
from api.models import (
    DailyReport, Contractor, Zone, Equipment,
    ReportContractor, ReportContractorZone, 
    EquipmentAssignment, Activity, Photo
)
import os
import random
from django.contrib.auth import get_user_model

# Récupérer l'utilisateur courant
User = get_user_model()
user = User.objects.first()

if not user:
    print("Aucun utilisateur trouvé dans le système.")
    exit()

print(f"Création de données pour l'utilisateur: {user.username}")

# Chemins des photos
photo_path1 = "C:/Users/marou/Desktop/DailyReporting/backend/backend/media/activity_photos/chantier1.jpg"
photo_path2 = "C:/Users/marou/Desktop/DailyReporting/backend/backend/media/activity_photos/chantier2.jpg"

# Vérifier si les fichiers existent
if not os.path.exists(photo_path1) or not os.path.exists(photo_path2):
    print("Les fichiers d'images n'existent pas aux chemins spécifiés.")
    exit()

# Lire les contenus des images une seule fois
with open(photo_path1, 'rb') as img_file:
    photo_content1 = img_file.read()
with open(photo_path2, 'rb') as img_file:
    photo_content2 = img_file.read()

# 1. Création des contractants
contractors_data = [
    {"name": "SOGEA"},
    {"name": "CEGELEC"},
    {"name": "SCIF"},
    {"name": "VINCI"}
]

contractors = []
for contractor_data in contractors_data:
    contractor, created = Contractor.objects.get_or_create(
        user=user,
        name=contractor_data["name"]
    )
    contractors.append(contractor)
    action = "Créé" if created else "Déjà existant"
    print(f"{action}: Contractant {contractor.name}")

# 2. Création des zones
zones_data = [
    {"name": "SA"},
    {"name": "SPA-06"},
    {"name": "HS-808"},
    {"name": "BT-101"},
    {"name": "MZ-240"},
    {"name": "PL-330"},
    {"name": "GR-450"},
    {"name": "TP-560"}
]

zones = []
for zone_data in zones_data:
    zone, created = Zone.objects.get_or_create(
        user=user,
        name=zone_data["name"]
    )
    zones.append(zone)
    action = "Créée" if created else "Déjà existante"
    print(f"{action}: Zone {zone.name}")

# 3. Création des équipements
equipments_data = [
    {"name": "Pelleteuse"},
    {"name": "Grue"},
    {"name": "Bulldozer"},
    {"name": "Compresseur"},
    {"name": "Béton-mixer"},
    {"name": "Échafaudage"},
    {"name": "Marteau piqueur"},
    {"name": "Groupe électrogène"},
    {"name": "Pompe à eau"},
    {"name": "Compacteur"}
]

equipments = []
for equipment_data in equipments_data:
    equipment, created = Equipment.objects.get_or_create(
        user=user,
        name=equipment_data["name"]
    )
    equipments.append(equipment)
    action = "Créé" if created else "Déjà existant"
    print(f"{action}: Équipement {equipment.name}")

# 4. Création des rapports journaliers
reports = []
today = date.today()

for i in range(8):
    report_date = today - timedelta(days=i)
    report, created = DailyReport.objects.get_or_create(
        user=user,
        date=report_date,
        defaults={"comments": f"Rapport de chantier du {report_date.strftime('%d/%m/%Y')}"}
    )
    reports.append(report)
    action = "Créé" if created else "Déjà existant"
    print(f"{action}: Rapport du {report_date}")

# 5. Création des relations et données
activities_data = [
    "Terrassement",
    "Fondations",
    "Montage structure",
    "Installation électricité",
    "Plomberie",
    "Pose de cloisons",
    "Peinture",
    "Carrelage",
    "Toiture",
    "Isolation",
    "Menuiserie",
    "Démolition",
    "Excavation",
    "Coffrage",
    "Ferraillage",
    "Bétonnage",
    "Installation sanitaire",
    "Pose de revêtement",
    "Montage d'équipements",
    "Aménagement extérieur"
]

activity_comments = [
    "Travaux en cours selon planning",
    "Retard causé par la pluie",
    "Avance sur le planning",
    "Besoin de matériaux supplémentaires",
    "Problème technique résolu",
    "Coordination avec autre équipe nécessaire",
    "Inspection réalisée avec succès",
    "Attente validation du client",
    "Conditions difficiles mais travaux maintenus",
    "Besoin d'ajustement technique"
]

# Pour chaque rapport, créer des liens avec contractants, zones, etc.
for report in reports:
    # Sélection de 2-3 contractants aléatoires
    selected_contractors = random.sample(contractors, random.randint(2, min(3, len(contractors))))
    
    for contractor in selected_contractors:
        # Création du lien rapport-contractant
        report_contractor, created = ReportContractor.objects.get_or_create(
            daily_report=report,
            contractor=contractor
        )
        action = "Créé" if created else "Déjà existant"
        print(f"{action}: Lien Rapport-Contractant pour {report.date} - {contractor.name}")
        
        # Sélection de 2-3 zones aléatoires
        selected_zones = random.sample(zones, random.randint(2, min(3, len(zones))))
        
        for zone in selected_zones:
            # Création du lien rapport-contractant-zone
            report_contractor_zone, created = ReportContractorZone.objects.get_or_create(
                report_contractor=report_contractor,
                zone=zone
            )
            action = "Créé" if created else "Déjà existant"
            print(f"{action}: Zone {zone.name} pour {contractor.name} le {report.date}")
            
            # Affectation de 2-3 équipements aléatoires
            selected_equipments = random.sample(equipments, random.randint(2, min(3, len(equipments))))
            
            for equipment in selected_equipments:
                # Création de l'affectation d'équipement
                equipment_assignment, created = EquipmentAssignment.objects.get_or_create(
                    report_contractor_zone=report_contractor_zone,
                    equipment=equipment,
                    defaults={"quantity": random.randint(1, 5)}
                )
                if not created:
                    equipment_assignment.quantity = random.randint(1, 5)
                    equipment_assignment.save()
                action = "Créé" if created else "Mis à jour"
                print(f"{action}: Équipement {equipment.name} ({equipment_assignment.quantity}) pour {zone.name}")
            
            # Création de 2-3 activités
            for _ in range(random.randint(2, 3)):
                activity_name = random.choice(activities_data)
                activity_comment = random.choice(activity_comments)
                
                activity = Activity.objects.create(
                    report_contractor_zone=report_contractor_zone,
                    name=activity_name,
                    comments=activity_comment
                )
                print(f"Créé: Activité {activity.name} pour {zone.name}")
                
                # Ajout des photos
                # Pour l'image 1
                photo1 = Photo(activity=activity)
                photo1.image.save(
                    f"activity_{activity.id}_photo1.jpg",
                    ContentFile(photo_content1),
                    save=True
                )
                print(f"Créé: Photo 1 pour {activity.name}")
                
                # Pour l'image 2
                photo2 = Photo(activity=activity)
                photo2.image.save(
                    f"activity_{activity.id}_photo2.jpg",
                    ContentFile(photo_content2),
                    save=True
                )
                print(f"Créé: Photo 2 pour {activity.name}")

print("Génération de données terminée avec succès.")