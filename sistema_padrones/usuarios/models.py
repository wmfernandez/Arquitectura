from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from django.core.validators import FileExtensionValidator

class EstadoHabilitacion(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Estados de Habilitación"

    history = HistoricalRecords()

class ConfiguracionPortal(models.Model):
    url_portal = models.URLField(default="https://portal.ejemplo.com", help_text="$URL_PORTAL")
    nombre_organismo = models.CharField(max_length=200, default="Intendencia de Ejemplo", help_text="$NOMBRE_ORGANISMO")
    sinonimo_sitio = models.CharField(max_length=200, default="El Portal", help_text="$SINONIMO_SITIO")
    direccion_organismo = models.CharField(max_length=255, default="Calle Falsa 123", help_text="$DIRECCION_ORGANISMO")
    mail_organismo = models.EmailField(default="contacto@ejemplo.com", help_text="$MAIL_ORGANISMO")
    texto_terminos_markdown = models.TextField(blank=True, null=True, help_text="Contenido base con variables (ej. $NOMBRE_ORGANISMO)")

    class Meta:
        verbose_name_plural = "Configuraciones del Portal"

    def __str__(self):
        return "Configuración del Portal"

    def get_terminos_renderizados(self):
        if not self.texto_terminos_markdown:
            return ""
        texto = self.texto_terminos_markdown
        texto = texto.replace("$URL_PORTAL", self.url_portal)
        texto = texto.replace("$NOMBRE_ORGANISMO", self.nombre_organismo)
        texto = texto.replace("$NOMBRE ORBANISMO", self.nombre_organismo) # catch typo en markdown original
        texto = texto.replace("$SINONIMO_SITIO", self.sinonimo_sitio)
        texto = texto.replace("$DIRECCION_ORGANISMO", self.direccion_organismo)
        texto = texto.replace("$MAIL_ORGANISMO", self.mail_organismo)
        return texto

    def save(self, *args, **kwargs):
        self.pk = 1 # Patrón Singleton: forzar siempre el id 1
        super().save(*args, **kwargs)

    history = HistoricalRecords()

class Profesion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Profesiones"

    history = HistoricalRecords()

class Profesional(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profesional')
    documento_identidad = models.CharField(max_length=20, unique=True, verbose_name="DNI/CI")
    matricula = models.CharField(max_length=50, unique=True)
    profesion = models.ForeignKey(Profesion, on_delete=models.PROTECT, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección / Domicilio")
    razon_social = models.CharField(max_length=150, blank=True, null=True, help_text="Completar si representa a una empresa")
    foto_dni_frente = models.FileField(
        upload_to='documentos/dni/', 
        blank=True, 
        null=True, 
        help_text="Foto o PDF",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'pdf'])]
    )
    foto_dni_reverso = models.FileField(
        upload_to='documentos/dni/', 
        blank=True, 
        null=True, 
        help_text="Foto o PDF",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'pdf'])]
    )
    
    estado_habilitacion = models.ForeignKey(EstadoHabilitacion, on_delete=models.PROTECT, null=True)
    observaciones_estado = models.TextField(blank=True, null=True, help_text="Motivo de rechazo, descarte o deshabilitación")
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultimo_acceso = models.DateTimeField(auto_now=True)

    def enviar_notificacion_estado(self, estado):
        from django.core.mail import send_mail
        from django.conf import settings
        import string
        import random
        
        usuario = self.usuario
        email = usuario.email
        if not email:
            return
            
        asunto = ""
        mensaje = ""
        
        if estado == 'HABILITADO':
            asunto = "Cuenta Habilitada en el Portal de Profesionales"
            mensaje = f"Hola {usuario.first_name},\n\nTu cuenta ha sido aprobada."
            if not usuario.has_usable_password():
                # Generar clave temporal
                chars = string.ascii_letters + string.digits
                password = ''.join(random.choice(chars) for _ in range(8))
                usuario.set_password(password)
                usuario.save()
                mensaje += f"\n\nTu contraseña temporal es: {password}\nPor favor, ingresá al portal y cámbiala desde tu perfil por seguridad."
                
        elif estado == 'OBSERVADO':
            asunto = "Tu cuenta en el Portal requiere atención"
            mensaje = f"Hola {usuario.first_name},\n\nTu cuenta ha sido marcada como OBSERVADA.\nMotivo: {self.observaciones_estado or 'No especificado'}\n\nPor favor inicia sesión con tu DNI para corregir estos datos en tu perfil."
            
        elif estado == 'SUSPENDIDO':
            asunto = "Cuenta Suspendida en el Portal de Profesionales"
            mensaje = f"Hola {usuario.first_name},\n\nTu cuenta ha sido SUSPENDIDA.\nMotivo: {self.observaciones_estado or 'No especificado'}\n\nPor favor inicia sesión o comunícate con la administración para más detalles."
            
        elif estado == 'RECHAZADO':
            asunto = "Solicitud de Registro Rechazada"
            mensaje = f"Hola {usuario.first_name},\n\nTu solicitud de registro ha sido RECHAZADA.\nMotivo: {self.observaciones_estado or 'No especificado'}\n\nAnte cualquier duda, comunícate con la administración."

        if asunto and mensaje:
            try:
                send_mail(
                    asunto, 
                    mensaje, 
                    getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@portalprofesionales.com'), 
                    [email], 
                    fail_silently=True
                )
            except Exception as e:
                print(f"Error enviando email: {e}")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_estado = None
        
        if not is_new:
            old_instance = Profesional.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.estado_habilitacion:
                old_estado = old_instance.estado_habilitacion.nombre.upper()
                
        # Sincronizar estado del usuario de Django según habilitación
        if self.estado_habilitacion:
            estado = self.estado_habilitacion.nombre.upper()
            self.usuario.is_active = estado in ['HABILITADO', 'OBSERVADO', 'SUSPENDIDO', 'LEVANTAR OBSERVACION', 'LEVANTAR SUSPENSION']
            self.usuario.save(update_fields=['is_active'])
            
        super().save(*args, **kwargs)
        
        # Enviar notificación si cambió el estado
        if self.estado_habilitacion:
            nuevo_estado = self.estado_habilitacion.nombre.upper()
            if old_estado != nuevo_estado:
                self.enviar_notificacion_estado(nuevo_estado)

    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.matricula}"

    class Meta:
        verbose_name_plural = "Profesionales"

    history = HistoricalRecords()
