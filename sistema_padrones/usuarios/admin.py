from django.contrib import admin
from .models import Profesional, EstadoHabilitacion, Profesion, ConfiguracionPortal
from simple_history.admin import SimpleHistoryAdmin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from django.core.validators import RegexValidator

@admin.register(ConfiguracionPortal)
class ConfiguracionPortalAdmin(SimpleHistoryAdmin):
    list_display = ('__str__', 'nombre_organismo', 'url_portal')
    
@admin.register(EstadoHabilitacion)
class EstadoHabilitacionAdmin(SimpleHistoryAdmin):
    list_display = ('nombre',)

@admin.register(Profesion)
class ProfesionAdmin(SimpleHistoryAdmin):
    list_display = ('nombre',)

from django.utils.html import mark_safe

@admin.register(Profesional)
class ProfesionalAdmin(SimpleHistoryAdmin):
    list_display = ('usuario', 'matricula', 'documento_identidad', 'estado_habilitacion', 'profesion')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'matricula', 'documento_identidad')
    list_filter = ('estado_habilitacion', 'profesion')
    readonly_fields = ('ver_foto_frente', 'ver_foto_reverso')
    
    fieldsets = (
        ('Datos de Usuario y Personales', {
            'fields': ('usuario', 'documento_identidad', 'telefono', 'direccion', 'razon_social')
        }),
        ('Datos Profesionales', {
            'fields': ('matricula', 'profesion')
        }),
        ('Documentación Adjunta (Sólo Lectura)', {
            'fields': ('ver_foto_frente', 'ver_foto_reverso')
        }),
        ('Estado de la Solicitud / Habilitación', {
            'fields': ('estado_habilitacion', 'observaciones_estado')
        }),
    )

    def ver_foto_frente(self, obj):
        if obj.foto_dni_frente:
            url = obj.foto_dni_frente.url
            if url.lower().endswith('.pdf'):
                return mark_safe(f'<a href="{url}" target="_blank" onclick="window.open(this.href, \'Modal\', \'width=800,height=600,left=\'+(screen.width/2-400)+\',top=\'+(screen.height/2-300)); return false;">Ver PDF (Frente) en ventana 800x600</a>')
            return mark_safe(f'''
                <a href="{url}" onclick="window.open(this.href, 'Modal', 'width=800,height=600,left='+(screen.width/2-400)+',top='+(screen.height/2-300)); return false;">
                    <img src="{url}" style="max-height: 150px; max-width: 300px; object-fit: contain; border: 1px solid #ccc; border-radius: 4px;" alt="Frente DNI" />
                </a>
                <br><small style="color: #666;">Click en la imagen para abrir en modal de 800x600</small>
            ''')
        return "No se ha adjuntado documento"
    ver_foto_frente.short_description = "DNI / CI (Frente)"

    def ver_foto_reverso(self, obj):
        if obj.foto_dni_reverso:
            url = obj.foto_dni_reverso.url
            if url.lower().endswith('.pdf'):
                return mark_safe(f'<a href="{url}" target="_blank" onclick="window.open(this.href, \'Modal\', \'width=800,height=600,left=\'+(screen.width/2-400)+\',top=\'+(screen.height/2-300)); return false;">Ver PDF (Reverso) en ventana 800x600</a>')
            return mark_safe(f'''
                <a href="{url}" onclick="window.open(this.href, 'Modal', 'width=800,height=600,left='+(screen.width/2-400)+',top='+(screen.height/2-300)); return false;">
                    <img src="{url}" style="max-height: 150px; max-width: 300px; object-fit: contain; border: 1px solid #ccc; border-radius: 4px;" alt="Reverso DNI" />
                </a>
                <br><small style="color: #666;">Click en la imagen para abrir en modal de 800x600</small>
            ''')
        return "No se ha adjuntado documento"
    ver_foto_reverso.short_description = "DNI / CI (Reverso)"

# Custom User Admin para cambiar "username" por "DNI/CI" en los formularios de creación/edición
dni_validator = RegexValidator(r'^\d+$', 'El DNI/CI debe contener únicamente números (sin puntos ni guiones).')

class CustomUserCreationForm(AdminUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].label = "DNI / CI"
            self.fields['username'].help_text = "Requerido. Únicamente números (sin puntos ni guiones)."
            self.fields['username'].validators = [dni_validator]

class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].label = "DNI / CI"
            self.fields['username'].help_text = "Requerido. Únicamente números (sin puntos ni guiones)."
            self.fields['username'].validators = [dni_validator]

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

# Re-registrar el modelo de Usuario
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
