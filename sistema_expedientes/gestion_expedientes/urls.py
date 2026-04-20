from django.urls import path
from .views import RecibirSolicitudAPIView

urlpatterns = [
    path('api/recibir-solicitud/', RecibirSolicitudAPIView.as_view(), name='recibir_solicitud'),
]
