from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle utilisateur.
    Utilisé pour convertir les objets CustomUser en format JSON.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 
                  'profile_picture', 'created_at', 'last_login_method']
        read_only_fields = ['id', 'created_at']
        

class FirebaseAuthSerializer(serializers.Serializer):
    """
    Serializer pour l'authentification Firebase.
    Valide le token ID Firebase envoyé par le frontend.
    """
    id_token = serializers.CharField(required=True)
    
    def validate_id_token(self, value):
        """Valide que le token est présent"""
        if not value:
            raise serializers.ValidationError("ID token is required")
        return value



from rest_framework import serializers
from .models import CustomUser

# Login classique avec email et mot de passe
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)