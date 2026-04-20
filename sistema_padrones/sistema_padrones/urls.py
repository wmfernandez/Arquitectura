"""
URL configuration for sistema_padrones project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from usuarios.views import CustomTokenObtainPairView
from usuarios.forms import DNIAuthenticationForm

admin.site.site_header = "Administración de Padrones"
admin.site.site_title = "Portal de Padrones"
admin.site.index_title = "Bienvenido al Sistema de Padrones"
admin.site.login_form = DNIAuthenticationForm

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('territorio.urls')),
    
    # Endpoints de Autenticación para el Portal React
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Endpoints de Usuarios/Profesionales
    path('api/', include('usuarios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
