from rest_framework import serializers
from .models import Expediente

class ExpedienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expediente
        fields = '__all__'

class RecibirSolicitudSerializer(serializers.Serializer):
    padron_referencia = serializers.CharField(max_length=50)
    solicitante_referencia = serializers.CharField(max_length=100)
    asunto_principal = serializers.CharField(max_length=255)
    tipo_tramite = serializers.CharField(max_length=150)
