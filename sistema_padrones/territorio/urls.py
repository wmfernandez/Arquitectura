from django.urls import path
from .views import get_padron_detalles, padrones_bbox, mis_solicitudes, get_form_options, buscar_padron
from .views import get_padron_detalles, padrones_bbox, mis_solicitudes, get_form_options, buscar_padron, enviar_solicitud

urlpatterns = [
    path('api/padron/detalles/<int:padron_id>/', get_padron_detalles, name='padron_detalles'),
    path('api/padrones_bbox/', padrones_bbox, name='padrones_bbox'),
    path('api/mis_solicitudes/', mis_solicitudes, name='mis_solicitudes'),
    path('api/form_options/', get_form_options, name='form_options'),
    path('api/padron/buscar/', buscar_padron, name='buscar_padron'),
    path('api/solicitudes/enviar/', enviar_solicitud, name='enviar_solicitud'),
]
