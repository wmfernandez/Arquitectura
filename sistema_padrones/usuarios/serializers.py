from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profesional, EstadoHabilitacion, ConfiguracionPortal, Profesion
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        
        user = User.objects.filter(username=username).first()
        if user and not user.is_active:
            if hasattr(user, 'profesional') and user.profesional.estado_habilitacion:
                estado = user.profesional.estado_habilitacion.nombre.upper()
                if estado == 'PENDIENTE':
                    raise AuthenticationFailed('Tu solicitud aún está pendiente de revisión.', code='authorization_pending')
                elif estado == 'SUSPENDIDO':
                    raise AuthenticationFailed('Tu cuenta ha sido suspendida.', code='account_suspended')
                elif estado == 'OBSERVADO':
                    raise AuthenticationFailed('Tu solicitud tiene observaciones y requiere atención.', code='account_observed')
                elif estado == 'RECHAZADO':
                    raise AuthenticationFailed('Tu solicitud de registro ha sido rechazada.', code='account_rejected')
        
        return super().validate(attrs)

class ProfesionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profesion
        fields = ['id', 'nombre']

class ConfiguracionPortalSerializer(serializers.ModelSerializer):
    terminos_y_condiciones = serializers.CharField(source='get_terminos_renderizados', read_only=True)
    class Meta:
        model = ConfiguracionPortal
        fields = ['terminos_y_condiciones']

class RegistroProfesionalSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(write_only=True)
    apellido = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    dni = serializers.CharField(source='documento_identidad')

    class Meta:
        model = Profesional
        fields = [
            'dni', 'matricula', 'profesion', 'telefono', 
            'direccion', 'razon_social', 'foto_dni_frente', 'foto_dni_reverso',
            'nombre', 'apellido', 'email'
        ]

    def validate_dni(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ya existe un usuario registrado con este DNI/CI.")
        if Profesional.objects.filter(documento_identidad=value).exists():
            raise serializers.ValidationError("Ya existe un profesional registrado con este DNI/CI.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario registrado con este correo electrónico.")
        return value

    def validate_matricula(self, value):
        if Profesional.objects.filter(matricula=value).exists():
            raise serializers.ValidationError("Ya existe un profesional registrado con esta matrícula.")
        return value

    def create(self, validated_data):
        nombre = validated_data.pop('nombre')
        apellido = validated_data.pop('apellido')
        email = validated_data.pop('email')
        
        # Crear usuario inactivo
        user = User(
            username=validated_data['documento_identidad'],
            first_name=nombre,
            last_name=apellido,
            email=email,
            is_active=False
        )
        user.set_unusable_password() # Se asiganará cuando sea aprobado
        user.save()

        # Asignar estado PENDIENTE
        estado_pendiente, _ = EstadoHabilitacion.objects.get_or_create(nombre='PENDIENTE', defaults={'descripcion': 'Esperando revisión del operador'})

        # Crear Profesional
        profesional = Profesional.objects.create(
            usuario=user,
            estado_habilitacion=estado_pendiente,
            **validated_data
        )
        return profesional

class PerfilProfesionalSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='usuario.first_name', required=False)
    apellido = serializers.CharField(source='usuario.last_name', required=False)
    email = serializers.EmailField(source='usuario.email', required=False)
    estado_nombre = serializers.CharField(source='estado_habilitacion.nombre', read_only=True)
    profesion_nombre = serializers.CharField(source='profesion.nombre', read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Profesional
        fields = [
            'documento_identidad', 'matricula', 'profesion', 'profesion_nombre', 'telefono', 
            'direccion', 'razon_social', 'foto_dni_frente', 'foto_dni_reverso',
            'nombre', 'apellido', 'email', 'estado_nombre', 'observaciones_estado', 'password'
        ]
        read_only_fields = ['documento_identidad', 'observaciones_estado', 'profesion_nombre']

    def validate_email(self, value):
        user = self.instance.usuario if self.instance else None
        query = User.objects.filter(email=value)
        if user:
            query = query.exclude(pk=user.pk)
        if query.exists():
            raise serializers.ValidationError("Ya existe otro usuario registrado con este correo electrónico.")
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if 'usuario' in validated_data:
            user_data = validated_data.pop('usuario')
            if 'first_name' in user_data:
                instance.usuario.first_name = user_data['first_name']
            if 'last_name' in user_data:
                instance.usuario.last_name = user_data['last_name']
            if 'email' in user_data:
                instance.usuario.email = user_data['email']
            instance.usuario.save()
            
        if password:
            instance.usuario.set_password(password)
            instance.usuario.save()
            
        return super().update(instance, validated_data)
