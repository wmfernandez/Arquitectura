from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.crypto import get_random_string
import datetime
from .models import Expediente, TipoTramiteExpediente, PrioridadExpediente, Oficina, EstadoExpediente, Movimiento, TipoMovimiento
from .serializers import RecibirSolicitudSerializer

class RecibirSolicitudAPIView(APIView):
    def post(self, request):
        serializer = RecibirSolicitudSerializer(data=request.data)
        if serializer.is_valid():
            datos = serializer.validated_data
            
            # Buscar o crear los datos paramétricos por defecto
            tipo_tramite, _ = TipoTramiteExpediente.objects.get_or_create(nombre=datos['tipo_tramite'])
            prioridad, _ = PrioridadExpediente.objects.get_or_create(nombre="Normal")
            oficina_entrada, _ = Oficina.objects.get_or_create(
                nombre_oficina="Mesa de Entrada", 
                defaults={'codigo_oficina': 'ME01'}
            )
            estado_inicial, _ = EstadoExpediente.objects.get_or_create(nombre="Iniciado")
            
            # Generar numero de expediente unico (ej: EXP-2026-XXXX)
            anio = datetime.datetime.now().year
            numero_random = get_random_string(length=6, allowed_chars='0123456789')
            nro_expediente = f"EXP-{anio}-{numero_random}"
            
            # Crear el expediente
            expediente = Expediente.objects.create(
                numero_expediente=nro_expediente,
                padron_referencia=datos['padron_referencia'],
                solicitante_referencia=datos['solicitante_referencia'],
                asunto_principal=datos['asunto_principal'],
                tipo_tramite=tipo_tramite,
                prioridad=prioridad,
                oficina_actual=oficina_entrada,
                estado_actual=estado_inicial,
                cantidad_fojas=1
            )
            
            # Registrar el movimiento inicial
            tipo_mov, _ = TipoMovimiento.objects.get_or_create(nombre="Inicio de Trámite")
            Movimiento.objects.create(
                expediente=expediente,
                oficina_destino=oficina_entrada,
                tipo_movimiento=tipo_mov,
                observaciones_del_pase="Expediente generado automáticamente desde el Sistema de Padrones."
            )
            
            return Response({
                "mensaje": "Expediente creado exitosamente.",
                "numero_expediente": expediente.numero_expediente,
                "id": expediente.id
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
