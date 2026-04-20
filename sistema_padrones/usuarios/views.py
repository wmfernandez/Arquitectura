from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegistroProfesionalSerializer, ConfiguracionPortalSerializer, ProfesionSerializer, CustomTokenObtainPairSerializer, PerfilProfesionalSerializer
from .models import ConfiguracionPortal, Profesion, EstadoHabilitacion

class PerfilProfesionalView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        if not hasattr(request.user, 'profesional'):
            return Response({"error": "No es un profesional"}, status=status.HTTP_403_FORBIDDEN)
        serializer = PerfilProfesionalSerializer(request.user.profesional)
        return Response(serializer.data)

    def put(self, request):
        if not hasattr(request.user, 'profesional'):
            return Response({"error": "No es un profesional"}, status=status.HTTP_403_FORBIDDEN)
            
        profesional = request.user.profesional
        serializer = PerfilProfesionalSerializer(profesional, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            # Change state to LEVANTAR OBSERVACION or LEVANTAR SUSPENSION if applicable
            if profesional.estado_habilitacion:
                estado_actual = profesional.estado_habilitacion.nombre.upper()
                nuevo_estado_nombre = None
                if estado_actual == 'OBSERVADO':
                    nuevo_estado_nombre = 'LEVANTAR OBSERVACION'
                elif estado_actual == 'SUSPENDIDO':
                    nuevo_estado_nombre = 'LEVANTAR SUSPENSION'
                    
                if nuevo_estado_nombre:
                    estado_nuevo, _ = EstadoHabilitacion.objects.get_or_create(nombre=nuevo_estado_nombre)
                    profesional.estado_habilitacion = estado_nuevo
                    profesional.save()
                    
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ProfesionListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        profesiones = Profesion.objects.all().order_by('nombre')
        serializer = ProfesionSerializer(profesiones, many=True)
        return Response(serializer.data)

class ConfiguracionPortalView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        config = ConfiguracionPortal.objects.first()
        if not config:
            return Response({"terminos_y_condiciones": "Términos y condiciones no configurados."})
        serializer = ConfiguracionPortalSerializer(config)
        return Response(serializer.data)

class RegistroProfesionalView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = RegistroProfesionalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"mensaje": "Registro creado exitosamente"}, status=status.HTTP_201_CREATED)
        return Response({"error": "Error de validación", "detalles": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
