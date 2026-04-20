from django.contrib import admin
from django.utils.html import format_html
from django.contrib.gis.admin import GISModelAdmin
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.forms.widgets import BaseGeometryWidget
from .models import Padron, Solicitud, TipoPadron, TipoTramite, EstadoSolicitud, ConfiguracionSolicitud, ArchivoTecnico
from simple_history.admin import SimpleHistoryAdmin

class PadronOSMWidget(BaseGeometryWidget):
    template_name = 'gis/admin/padron_osm.html'
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.map_width = 800
        self.map_height = 500
        self.display_raw = False
        self.modifiable = False # Esto es clave para deshabilitar las herramientas en ModelAdmin

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        # Leaflet EXIGE estrictamente EPSG:4326 (Lat/Lon) para GeoJSON.
        # Si la DB o el modelo usan 3857 u otro, lo transformamos aquí en el backend.
        if value:
            # Clonamos para no afectar la instancia original en memoria
            geom = value.clone()
            if geom.srid != 4326:
                geom.transform(4326)
            context['serialized'] = geom.geojson
        else:
            context['serialized'] = ''
        return context

class SeccionCatastralFilter(admin.SimpleListFilter):
    title = 'Sección Catastral'
    parameter_name = 'seccat'

    def lookups(self, request, model_admin):
        # Obtenemos secciones únicas directamente del JSONField usando PostgreSQL
        secciones = set(
            Padron.objects.filter(atributos_gis__has_key='SECCAT')
            .values_list('atributos_gis__SECCAT', flat=True)
        )
        # Filtramos None o vacíos y los ordenamos
        validas = [s for s in secciones if s is not None and str(s).strip() != '']
        try:
            validas = sorted(validas, key=lambda x: int(x) if str(x).isdigit() else x)
        except:
            validas = sorted(str(v) for v in validas)
            
        return [(str(s), str(s)) for s in validas]

    def queryset(self, request, queryset):
        if self.value():
            val = self.value()
            # El valor en el JSON puede estar como entero o como string
            if val.isdigit():
                return queryset.filter(atributos_gis__SECCAT=int(val)) | queryset.filter(atributos_gis__SECCAT=val)
            return queryset.filter(atributos_gis__SECCAT=val)
        return queryset

@admin.register(TipoPadron)
class TipoPadronAdmin(SimpleHistoryAdmin):
    list_display = ('nombre',)

@admin.register(TipoTramite)
class TipoTramiteAdmin(SimpleHistoryAdmin):
    list_display = ('nombre',)

@admin.register(EstadoSolicitud)
class EstadoSolicitudAdmin(SimpleHistoryAdmin):
    list_display = ('nombre', 'descripcion')

@admin.register(Padron)
class PadronAdmin(SimpleHistoryAdmin):
    # Heredamos directamente de SimpleHistoryAdmin (que ya hereda de ModelAdmin)
    # Ya no heredamos de GISModelAdmin porque tiene hardcodeos que ignoran nuestros widgets
    
    formfield_overrides = {
        gis_models.MultiPolygonField: {'widget': PadronOSMWidget},
        gis_models.PolygonField: {'widget': PadronOSMWidget},
    }
    
    list_display = ('numero_padron', 'tipo_padron', 'departamento', 'mostrar_ubicacion', 'mostrar_seccion', 'mostrar_area', 'mostrar_valor')
    search_fields = ('=numero_padron', 'departamento', 'localidad')
    list_filter = ('tipo_padron', 'departamento', 'localidad', SeccionCatastralFilter)

    readonly_fields = ('mostrar_ubicacion', 'mostrar_seccion', 'mostrar_area', 'mostrar_valor')

    fieldsets = (
        ('Datos Principales', {
            'fields': ('numero_padron', 'tipo_padron', 'departamento')
        }),
        ('Información Geográfica (Calculada)', {
            'fields': ('mostrar_ubicacion', 'mostrar_seccion', 'mostrar_area', 'mostrar_valor', 'atributos_gis')
        }),
        ('Geometría Mapeada', {
            'fields': ('geometria',)
        }),
        ('Datos Manuales Base (Opcionales)', {
            'classes': ('collapse',),
            'fields': ('localidad', 'barrio', 'direccion_fisica', 'area_metros_cuadrados', 'valor_catastral')
        }),
    )

    def mostrar_ubicacion(self, obj):
        return obj.ubicacion_mostrar
    mostrar_ubicacion.short_description = "Localidad/Barrio"

    def mostrar_seccion(self, obj):
        return obj.seccion_catastral
    mostrar_seccion.short_description = "Secc. Catastral"

    def mostrar_area(self, obj):
        return obj.area_formateada
    mostrar_area.short_description = "Área"

    def mostrar_valor(self, obj):
        if obj.valor_catastral_real:
            return f"${obj.valor_catastral_real:,.2f}"
        return "N/A"
    mostrar_valor.short_description = "Valor Catastral"

    class Media:
        js = ('js/padron_map_style.js',)

from django import forms

class SolicitudAdminForm(forms.ModelForm):
    filtro_tipo_padron = forms.ModelChoiceField(
        queryset=TipoPadron.objects.all(),
        required=False,
        label="1. Filtrar por Tipo de Padrón"
    )
    filtro_localidad = forms.ChoiceField(
        required=False,
        label="2. Filtrar por Localidad",
        help_text="Opcional. Seleccione si es Urbano."
    )

    class Meta:
        model = Solicitud
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        localidades = set(Padron.objects.exclude(localidad__isnull=True).exclude(localidad='').values_list('localidad', flat=True))
        localidades = sorted([l for l in localidades if l])
        self.fields['filtro_localidad'].choices = [('', '---------')] + [(l, l) for l in localidades]

class ArchivoTecnicoInline(admin.TabularInline):
    model = ArchivoTecnico
    extra = 0
    readonly_fields = ('nombre_original', 'tamano_bytes', 'fecha_subida', 'archivo_link')
    fields = ('archivo_link', 'nombre_original', 'tamano_bytes', 'fecha_subida')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def archivo_link(self, obj):
        if obj.archivo:
            return format_html('<a href="{0}" target="_blank">Ver Archivo</a>', obj.archivo.url)
        return "N/A"
    archivo_link.short_description = "Archivo"

@admin.register(Solicitud)
class SolicitudAdmin(SimpleHistoryAdmin):
    form = SolicitudAdminForm
    list_display = ('id', 'padron', 'profesional', 'tipo_tramite', 'estado_solicitud', 'numero_expediente_generado')
    search_fields = ('padron__numero_padron', 'profesional__matricula', 'numero_expediente_generado')
    list_filter = ('estado_solicitud', 'tipo_tramite')
    
    inlines = [ArchivoTecnicoInline]

    raw_id_fields = ('padron',)
    autocomplete_fields = ('profesional',)

    fieldsets = (
        ('Selección de Padrón', {
            'fields': ('filtro_tipo_padron', 'filtro_localidad', 'padron')
        }),
        ('Detalles de la Solicitud', {
            'fields': ('profesional', 'tipo_tramite', 'descripcion_detallada')
        }),
        ('Estado e Integración', {
            'fields': ('estado_solicitud', 'numero_expediente_generado', 'fecha_envio_sistema_b', 'observaciones_rechazo')
        }),
    )

    class Media:
        js = ('js/solicitud_padron_filter.js',)

@admin.register(ConfiguracionSolicitud)
class ConfiguracionSolicitudAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tamano_maximo_archivo_mb', 'tamano_maximo_total_mb')

    def has_add_permission(self, request):
        return not ConfiguracionSolicitud.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
