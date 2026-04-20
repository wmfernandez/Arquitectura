from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import Profesional

class DNIAuthBackend(ModelBackend):
    """
    Permite a los profesionales iniciar sesión utilizando su DNI (documento_identidad)
    en lugar del username tradicional de Django.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # El frontend envía el DNI en la variable "username"
        try:
            profesional = Profesional.objects.get(documento_identidad=username)
            user = profesional.usuario
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Profesional.DoesNotExist:
            return None
        return None
