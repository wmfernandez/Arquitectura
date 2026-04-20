from django.contrib.gis.db import models
from usuarios.models import Profesional
from simple_history.models import HistoricalRecords
import requests
from django.utils import timezone

class TipoPadron(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.nombre

    class Meta:
        verbose_name_plural = "Tipos de Padrón"

    history = HistoricalRecords()

class Padron(models.Model):
    numero_padron = models.CharField(max_length=50)
    geometria = models.MultiPolygonField(srid=4326, blank=True, null=True) # WSG84
    atributos_gis = models.JSONField(blank=True, null=True, help_text="Propiedades originales del GeoJSON")
    
    departamento = models.CharField(max_length=100)
    localidad = models.CharField(max_length=100)
    barrio = models.CharField(max_length=100, blank=True, null=True)
    direccion_fisica = models.CharField(max_length=255, blank=True, null=True)
    
    tipo_padron = models.ForeignKey(TipoPadron, on_delete=models.PROTECT, null=True)
    area_metros_cuadrados = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    valor_catastral = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    @property
    def area_formateada(self):
        if not self.atributos_gis:
            return "N/A"
        if self.tipo_padron and self.tipo_padron.nombre.lower() == "rural":
            ha = self.atributos_gis.get('AREAHA', 0)
            mc = self.atributos_gis.get('AREAMC', 0)
            return f"{ha} ha y {mc} m²"
        else:
            area = self.atributos_gis.get('AREA', 0)
            return f"{area} m²"

    @property
    def valor_catastral_real(self):
        if not self.atributos_gis:
            return self.valor_catastral
        return self.atributos_gis.get('VALCAT', self.valor_catastral)

    @property
    def seccion_catastral(self):
        if not self.atributos_gis:
            return "N/A"
        return self.atributos_gis.get('SECCAT', "N/A")

    @property
    def ubicacion_mostrar(self):
        if self.tipo_padron and self.tipo_padron.nombre.lower() == "rural":
            return "Zona Rural"
        return self.localidad

    def __str__(self):
        tipo = self.tipo_padron.nombre if self.tipo_padron else "N/A"
        return f"Padrón N° {self.numero_padron} ({tipo}) - {self.ubicacion_mostrar} - Secc. {self.seccion_catastral}"

    class Meta:
        verbose_name_plural = "Padrones"

    history = HistoricalRecords()

class TipoTramite(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    def __str__(self): return self.nombre

    class Meta:
        verbose_name_plural = "Tipos de Trámite"

    history = HistoricalRecords()

class EstadoSolicitud(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    def __str__(self): return self.nombre

    class Meta:
        verbose_name_plural = "Estados de Solicitud"

    history = HistoricalRecords()

class Solicitud(models.Model):
    profesional = models.ForeignKey(Profesional, on_delete=models.PROTECT, related_name='solicitudes')
    padron = models.ForeignKey(Padron, on_delete=models.PROTECT, related_name='solicitudes', verbose_name="ID Padrón")
    
    tipo_tramite = models.ForeignKey(TipoTramite, on_delete=models.PROTECT, null=True)
    descripcion_detallada = models.TextField(blank=True, null=True)
    
    estado_solicitud = models.ForeignKey(EstadoSolicitud, on_delete=models.PROTECT, null=True)
    observaciones_rechazo = models.TextField(blank=True, null=True, help_text="Razón del rechazo si el Sistema B no acepta el trámite")
    
    numero_expediente_generado = models.CharField(max_length=50, blank=True, null=True, help_text="Referencia al Sistema B")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)
    fecha_envio_sistema_b = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        enviar_a_expedientes = False
        if self.pk:
            # Check if status changed to ENVIADA
            old_instance = Solicitud.objects.get(pk=self.pk)
            if old_instance.estado_solicitud != self.estado_solicitud and self.estado_solicitud and self.estado_solicitud.nombre.upper() == 'ENVIADA':
                enviar_a_expedientes = True
        elif self.estado_solicitud and self.estado_solicitud.nombre.upper() == 'ENVIADA':
            # It's new and status is ENVIADA
            enviar_a_expedientes = True

        super().save(*args, **kwargs)

        if enviar_a_expedientes and not self.numero_expediente_generado:
            try:
                # Docker network URL
                url = 'http://api_expedientes:8000/api/recibir-solicitud/'
                payload = {
                    "padron_referencia": str(self.padron.numero_padron),
                    "solicitante_referencia": str(self.profesional.matricula),
                    "asunto_principal": self.descripcion_detallada or f"Trámite sobre padrón {self.padron.numero_padron}",
                    "tipo_tramite": self.tipo_tramite.nombre if self.tipo_tramite else "Trámite General"
                }
                response = requests.post(url, json=payload, headers={'Host': 'localhost'}, timeout=10)
                
                if response.status_code == 201:
                    data = response.json()
                    self.numero_expediente_generado = data.get('numero_expediente')
                    self.fecha_envio_sistema_b = timezone.now()
                    # Resave to update the expediente number without triggering the if condition again
                    super().save(update_fields=['numero_expediente_generado', 'fecha_envio_sistema_b'])
                else:
                    self.observaciones_rechazo = f"Error en API (Status {response.status_code}): {response.text}"
                    super().save(update_fields=['observaciones_rechazo'])
            except Exception as e:
                self.observaciones_rechazo = f"Excepción de conexión: {str(e)}"
                super().save(update_fields=['observaciones_rechazo'])

    def __str__(self):
        return f"Solicitud {self.id} - Padrón {self.padron.numero_padron}"

    class Meta:
        verbose_name_plural = "Solicitudes"

    history = HistoricalRecords()

class ConfiguracionSolicitud(models.Model):
    extensiones_permitidas = models.CharField(max_length=255, default='.pdf,.zip,.rar', help_text="Separadas por coma (ej: .pdf,.zip)")
    tamano_maximo_archivo_mb = models.DecimalField(max_digits=5, decimal_places=2, default=10.0, help_text="Tamaño máximo por archivo en MB")
    tamano_maximo_total_mb = models.DecimalField(max_digits=5, decimal_places=2, default=50.0, help_text="Suma total máxima de archivos por solicitud en MB")

    def save(self, *args, **kwargs):
        self.pk = 1 # Ensure only one instance exists
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Configuraciones de Solicitudes"

    class Meta:
        verbose_name = "Parámetros de Solicitudes"
        verbose_name_plural = "Configuraciones de Solicitudes"

class ArchivoTecnico(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='archivos')
    archivo = models.FileField(upload_to='archivos_tecnicos/%Y/%m/')
    nombre_original = models.CharField(max_length=255)
    tamano_bytes = models.BigIntegerField()
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Archivo {self.nombre_original} (Solicitud {self.solicitud_id})"
