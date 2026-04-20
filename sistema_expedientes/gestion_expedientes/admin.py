from django.contrib import admin
from .models import Oficina, Expediente, Movimiento, DocumentoAdjunto, PrioridadExpediente, EstadoExpediente, TipoTramiteExpediente, TipoMovimiento
from simple_history.admin import SimpleHistoryAdmin

@admin.register(PrioridadExpediente)
class PrioridadExpedienteAdmin(SimpleHistoryAdmin):
    list_display = ('nombre',)

@admin.register(EstadoExpediente)
class EstadoExpedienteAdmin(SimpleHistoryAdmin):
    list_display = ('nombre',)

@admin.register(TipoTramiteExpediente)
class TipoTramiteExpedienteAdmin(SimpleHistoryAdmin):
    list_display = ('nombre',)

@admin.register(TipoMovimiento)
class TipoMovimientoAdmin(SimpleHistoryAdmin):
    list_display = ('nombre',)

@admin.register(Oficina)
class OficinaAdmin(SimpleHistoryAdmin):
    list_display = ('codigo_oficina', 'nombre_oficina', 'es_activa')
    search_fields = ('codigo_oficina', 'nombre_oficina')

@admin.register(Expediente)
class ExpedienteAdmin(SimpleHistoryAdmin):
    list_display = ('numero_expediente', 'asunto_principal', 'estado_actual', 'oficina_actual', 'prioridad')
    search_fields = ('numero_expediente', 'asunto_principal', 'padron_referencia')
    list_filter = ('estado_actual', 'prioridad', 'oficina_actual')

@admin.register(Movimiento)
class MovimientoAdmin(SimpleHistoryAdmin):
    list_display = ('expediente', 'oficina_origen', 'oficina_destino', 'tipo_movimiento', 'fecha_envio')
    search_fields = ('expediente__numero_expediente',)
    list_filter = ('tipo_movimiento',)

@admin.register(DocumentoAdjunto)
class DocumentoAdjuntoAdmin(SimpleHistoryAdmin):
    list_display = ('nombre_documento', 'expediente', 'usuario_que_subio', 'fecha_subida')
    search_fields = ('nombre_documento', 'expediente__numero_expediente')
