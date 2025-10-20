from django.urls import path ,include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')


urlpatterns = [
    # Endpoint pour l'authentification Firebase
    path('firebase-login/', views.firebase_login, name='firebase_login'),
    
    # Endpoint pour récupérer le profil utilisateur
    path('profile/', views.user_profile, name='user_profile'),
    
    # Endpoint pour rafraîchir le token JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('update-username/', views.update_username, name='update_username'),
    
    path('check-username/', views.check_username, name='check_username'),

    # Ajoute les routes du router (ViewSet)
    path('', include(router.urls)),

]