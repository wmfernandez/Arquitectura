from django.urls import path
from .views import RegistroProfesionalView, ConfiguracionPortalView, ProfesionListView, PerfilProfesionalView

urlpatterns = [
    path('registro-profesional/', RegistroProfesionalView.as_view(), name='registro_profesional'),
    path('configuracion-portal/', ConfiguracionPortalView.as_view(), name='configuracion_portal'),
    path('profesiones/', ProfesionListView.as_view(), name='lista_profesiones'),
    path('perfil/', PerfilProfesionalView.as_view(), name='perfil'),
]
