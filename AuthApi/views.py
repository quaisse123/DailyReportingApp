from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from firebase_admin import auth as firebase_auth
from .models import CustomUser
from .serializers import UserSerializer, FirebaseAuthSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def firebase_login(request):
    """
    Vue pour authentifier un utilisateur avec Firebase.
    
    Processus:
    1. Reçoit le token ID Firebase du frontend
    2. Vérifie le token avec Firebase Admin
    3. Récupère les informations utilisateur
    4. Crée ou met à jour l'utilisateur Django
    5. Génère un token JWT Django
    6. Retourne le token et les infos utilisateur
    """
    # Valide les données de la requête
    serializer = FirebaseAuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Récupère le token ID Firebase
    id_token = serializer.validated_data['id_token']
    
    try:
        # Vérifie le token auprès de Firebase
        decoded_token = firebase_auth.verify_id_token(id_token)
        
        # Récupère les informations utilisateur
        firebase_uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        name = decoded_token.get('name', '')
        picture = decoded_token.get('picture', '')
        
        # Divise le nom complet en prénom/nom si disponible
        if ' ' in name:
            first_name, last_name = name.rsplit(' ', 1)
        else:
            first_name, last_name = name, ''
        
        # Crée ou récupère l'utilisateur Django
        try:
            # Essaye de trouver l'utilisateur par firebase_uid
            user = CustomUser.objects.get(firebase_uid=firebase_uid)
            # Met à jour les informations si nécessaire
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.profile_picture = picture
            user.save()
            
        except CustomUser.DoesNotExist:
            # Essaye de trouver l'utilisateur par email
            try:
                user = CustomUser.objects.get(email=email)
                # Associe l'ID Firebase à cet utilisateur
                user.firebase_uid = firebase_uid
                user.first_name = first_name
                user.last_name = last_name
                user.profile_picture = picture
                user.save()
            except CustomUser.DoesNotExist:
                # Crée un nouvel utilisateur
                username = email.split('@')[0]
                # Assure que le username est unique
                base_username = username
                counter = 1
                while CustomUser.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    firebase_uid=firebase_uid,
                    first_name=first_name,
                    last_name=last_name,
                    profile_picture=picture
                )
        
        # Génère des tokens JWT pour l'authentification Django
        refresh = RefreshToken.for_user(user)
        
        # Prépare la réponse
        user_data = UserSerializer(user).data
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        print("Authentification réussie, tokens JWT générés")
        return Response({
            'user': user_data,
            'tokens': tokens
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        # Gère les erreurs (token invalide, expiré, etc.)
        return Response({
            'error': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Vue pour récupérer le profil de l'utilisateur connecté.
    Nécessite un token JWT valide.
    """
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_username (request):
    """
    Vue pour mettre à jour le nom d'utilisateur de l'utilisateur connecté.
    Nécessite un token JWT valide.
    """
    if request.method == 'POST':
        new_username = request.data.get('username', '').strip()
        if not new_username:
            return Response({'error': 'Le nom d\'utilisateur ne peut pas être vide.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if CustomUser.objects.filter(username=new_username).exclude(id=request.user.id).exists():
            return Response({'error': 'Ce nom d\'utilisateur est déjà pris.'}, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.username = new_username
        request.user.save()
        return Response({'message': 'Nom d\'utilisateur mis à jour avec succès.'}, status=status.HTTP_200_OK)
    
    return Response({'error': 'Méthode non autorisée.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def check_username(request):
    username = request.GET.get('username', '').strip()
    exists = CustomUser.objects.filter(username=username).exists()
    return Response({'available': not exists})

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserSerializer, LoginSerializer

class UserViewSet(viewsets.ViewSet):
    queryset = CustomUser.objects.all()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        # À compléter selon ton UserSerializer
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=request.data['password'],
            first_name=serializer.validated_data.get('first_name', ''),
            last_name=serializer.validated_data.get('last_name', ''),
        )
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        return Response(UserSerializer(request.user).data)