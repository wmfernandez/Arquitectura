from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

class Oficina(models.Model):
    nombre_oficina = models.CharField(max_length=150, unique=True)
    codigo_oficina = models.CharField(max_length=20, unique=True)
    es_activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo_oficina} - {self.nombre_oficina}"

    class Meta:
        verbose_name_plural = "Oficinas"

    history = HistoricalRecords()

class PrioridadExpediente(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.nombre

    class Meta:
        verbose_name_plural = "Prioridades de Expediente"

    history = HistoricalRecords()

class EstadoExpediente(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.nombre

    class Meta:
        verbose_name_plural = "Estados de Expediente"

    history = HistoricalRecords()

class TipoTramiteExpediente(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    def __str__(self): return self.nombre

    class Meta:
        verbose_name_plural = "Tipos de Trámite de Expediente"

    history = HistoricalRecords()

class Expediente(models.Model):
    numero_expediente = models.CharField(max_length=50, unique=True)
    
    padron_referencia = models.CharField(max_length=50, help_text="ID o número de padrón del Sistema GIS")
    solicitante_referencia = models.CharField(max_length=100, help_text="DNI o Matrícula del Profesional")
    
    asunto_principal = models.CharField(max_length=255)
    tipo_tramite = models.ForeignKey(TipoTramiteExpediente, on_delete=models.PROTECT, null=True)
    
    prioridad = models.ForeignKey(PrioridadExpediente, on_delete=models.PROTECT, null=True)
    oficina_actual = models.ForeignKey(Oficina, on_delete=models.PROTECT, related_name='expedientes_actuales')
    cantidad_fojas = models.PositiveIntegerField(default=1)
    
    estado_actual = models.ForeignKey(EstadoExpediente, on_delete=models.PROTECT, null=True)
    
    fecha_caratulado = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(blank=True, null=True)
    fecha_vencimiento_plazo = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.numero_expediente

    class Meta:
        verbose_name_plural = "Expedientes"

    history = HistoricalRecords()

class TipoMovimiento(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.nombre

    class Meta:
        verbose_name_plural = "Tipos de Movimiento"

    history = HistoricalRecords()

class Movimiento(models.Model):
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='movimientos')
    
    oficina_origen = models.ForeignKey(Oficina, on_delete=models.PROTECT, related_name='movimientos_origen', blank=True, null=True)
    oficina_destino = models.ForeignKey(Oficina, on_delete=models.PROTECT, related_name='movimientos_destino')
    
    usuario_que_envia = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pases_enviados', blank=True, null=True)
    usuario_que_recibe = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pases_recibidos', blank=True, null=True)
    
    tipo_movimiento = models.ForeignKey(TipoMovimiento, on_delete=models.PROTECT, null=True)
    fojas_agregadas = models.PositiveIntegerField(default=0)
    observaciones_del_pase = models.TextField(blank=True, null=True)
    
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_recepcion = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Movimiento {self.id} - Expediente {self.expediente.numero_expediente}"

    class Meta:
        verbose_name_plural = "Movimientos"

    history = HistoricalRecords()

class DocumentoAdjunto(models.Model):
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='documentos')
    # Requiere configurar MEDIA_ROOT en settings.py
    archivo_adjunto = models.FileField(upload_to='documentos_expedientes/%Y/%m/')
    nombre_documento = models.CharField(max_length=255)
    
    usuario_que_subio = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_documento} (Exp: {self.expediente.numero_expediente})"

    class Meta:
        verbose_name_plural = "Documentos Adjuntos"

    history = HistoricalRecords()
