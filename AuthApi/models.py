from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Modèle utilisateur personnalisé qui étend l'utilisateur Django standard.
    
    Attributs:
        firebase_uid (str): L'identifiant unique Firebase de l'utilisateur
        profile_picture (str): URL de la photo de profil (généralement de Google)
        created_at (datetime): Date de création du compte
        last_login_method (str): Méthode de dernière connexion (google, email, etc.)
    """
    firebase_uid = models.CharField(max_length=128, blank=True, null=True, unique=True)
    profile_picture = models.URLField(max_length=1024, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_method = models.CharField(max_length=50, default='google')
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        """Retourne l'email comme représentation string de l'utilisateur"""
        return self.email