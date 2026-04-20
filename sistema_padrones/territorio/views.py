from django.http import JsonResponse
from django.contrib.gis.geos import Polygon
from .models import Padron, Solicitud, TipoPadron, TipoTramite
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import json

def get_padron_detalles(request, padron_id):
    try:
        padron = Padron.objects.get(pk=padron_id)
        return JsonResponse({'detalles': str(padron)})
    except Padron.DoesNotExist:
        return JsonResponse({'detalles': ''}, status=404)

def padrones_bbox(request):
    bbox_str = request.GET.get('bbox')
    exclude_padron = request.GET.get('exclude')
    
    if not bbox_str:
        return JsonResponse({'type': 'FeatureCollection', 'features': []})
    
    try:
        # El BBOX viene de Leaflet en formato EPSG:4326 (WGS84): oeste, sur, este, norte
        xmin, ymin, xmax, ymax = map(float, bbox_str.split(','))
        bbox = Polygon.from_bbox((xmin, ymin, xmax, ymax))
        bbox.srid = 4326  # Aseguramos a Django que el BBOX está en Lat/Lon
        
        # Filtramos los padrones que se intersectan con el rectángulo de la pantalla
        # Django GIS se encarga automáticamente de las transformaciones (ej. BBOX 4326 vs DB 3857)
        qs = Padron.objects.filter(geometria__bboverlaps=bbox)
        
        # Excluimos el padrón actual para no dibujarlo dos veces (ya lo dibuja el widget)
        if exclude_padron:
            qs = qs.exclude(numero_padron=exclude_padron)
            
        features = []
        # Limitamos a 500 polígonos para proteger el rendimiento del navegador
        for p in qs[:500]:
            if p.geometria:
                geom = p.geometria.clone()
                if geom.srid != 4326:
                    geom.transform(4326) # Mandamos a Leaflet en 4326
                
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geom.geojson),
                    "properties": {
                        "numero_padron": p.numero_padron,
                        "tipo": p.tipo_padron.nombre.lower() if p.tipo_padron else ""
                    }
                })
                
        return JsonResponse({'type': 'FeatureCollection', 'features': features})
    except Exception as e:
        return Response({'error': str(e)}, status=500)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enviar_solicitud(request):
    try:
        profesional = request.user.profesional
        if not profesional.estado_habilitacion or profesional.estado_habilitacion.nombre.upper() != 'HABILITADO':
            return Response({'error': 'Profesional no habilitado para enviar solicitudes.'}, status=403)
    except:
        return Response({'error': 'El usuario no es un profesional válido.'}, status=403)

    padron_id = request.data.get('padron_id')
    tipo_tramite_id = request.data.get('tipo_tramite_id')
    archivos = request.FILES.getlist('archivos')

    if not padron_id or not tipo_tramite_id:
        return Response({'error': 'Padrón y Tipo de Trámite son obligatorios.'}, status=400)

    try:
        padron = Padron.objects.get(id=padron_id)
        tipo_tramite = TipoTramite.objects.get(id=tipo_tramite_id)
    except (Padron.DoesNotExist, TipoTramite.DoesNotExist):
        return Response({'error': 'Padrón o Tipo de Trámite inválido.'}, status=400)

    from .models import ConfiguracionSolicitud, ArchivoTecnico, EstadoSolicitud
    config = ConfiguracionSolicitud.load()
    
    # Validar archivos en el backend
    total_mb = 0
    extensiones_permitidas = [e.strip().lower() for e in config.extensiones_permitidas.split(',')]

    for archivo in archivos:
        ext = '.' + archivo.name.split('.')[-1].lower() if '.' in archivo.name else ''
        if ext not in extensiones_permitidas:
            return Response({'error': f'El archivo {archivo.name} tiene una extensión no permitida.'}, status=400)
        
        size_mb = archivo.size / (1024 * 1024)
        if size_mb > config.tamano_maximo_archivo_mb:
            return Response({'error': f'El archivo {archivo.name} excede el máximo permitido.'}, status=400)
        
        total_mb += size_mb

    if total_mb > config.tamano_maximo_total_mb:
        return Response({'error': 'El tamaño total de los archivos excede el máximo permitido.'}, status=400)

    # Crear la solicitud
    estado_ingresada, _ = EstadoSolicitud.objects.get_or_create(nombre='INGRESADA', defaults={'descripcion': 'Solicitud ingresada por el profesional'})
    
    solicitud = Solicitud.objects.create(
        profesional=profesional,
        padron=padron,
        tipo_tramite=tipo_tramite,
        estado_solicitud=estado_ingresada,
        descripcion_detallada=f'Solicitud creada desde Portal de Profesionales.'
    )

    # Guardar archivos
    for archivo in archivos:
        ArchivoTecnico.objects.create(
            solicitud=solicitud,
            archivo=archivo,
            nombre_original=archivo.name,
            tamano_bytes=archivo.size
        )

    return Response({
        'message': 'Solicitud enviada correctamente',
        'solicitud_id': solicitud.id
    }, status=201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_solicitudes(request):
    try:
        profesional = request.user.profesional
    except AttributeError:
        return Response({'error': 'El usuario no tiene un perfil de profesional asociado.'}, status=403)
        
    solicitudes = Solicitud.objects.filter(profesional=profesional).order_by('-fecha_creacion')
    data = []
    for sol in solicitudes:
        data.append({
            'id': sol.id,
            'padron': sol.padron.numero_padron if sol.padron else 'N/A',
            'tramite': sol.tipo_tramite.nombre if sol.tipo_tramite else 'N/A',
            'estado': sol.estado_solicitud.nombre if sol.estado_solicitud else 'Pendiente',
            'fecha': sol.fecha_creacion.strftime('%Y-%m-%d'),
            'numero_expediente': sol.numero_expediente_generado
        })
        
    return Response({
        'user': {
            'name': request.user.get_full_name() or request.user.username,
            'role': profesional.profesion.nombre if profesional.profesion else 'Profesional',
            'matricula': profesional.matricula
        },
        'solicitudes': data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_form_options(request):
    tipos = list(TipoPadron.objects.values('id', 'nombre'))
    
    # Extraer localidades únicas de padrones urbanos
    localidades = Padron.objects.filter(tipo_padron__nombre__icontains='urbano')\
                                .values_list('localidad', flat=True)\
                                .distinct().order_by('localidad')
                                
    tipos_tramite = list(TipoTramite.objects.values('id', 'nombre'))
    
    from .models import ConfiguracionSolicitud
    config = ConfiguracionSolicitud.load()
                                
    return Response({
        'tipos_padron': tipos,
        'localidades': list(localidades),
        'tipos_tramite': tipos_tramite,
        'configuracion': {
            'extensiones_permitidas': config.extensiones_permitidas,
            'tamano_maximo_archivo_mb': float(config.tamano_maximo_archivo_mb),
            'tamano_maximo_total_mb': float(config.tamano_maximo_total_mb)
        }
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def buscar_padron(request):
    numero = request.GET.get('numero', '')
    tipo_id = request.GET.get('tipo_id', '')
    localidad = request.GET.get('localidad', '')
    
    if not numero:
        return Response({'error': 'El número de padrón es requerido'}, status=400)
        
    query = Padron.objects.filter(numero_padron=numero)
    
    if tipo_id:
        query = query.filter(tipo_padron_id=tipo_id)
        
    if localidad:
        # Solo aplicamos localidad si se especificó y si es de un tipo que la requiera (ej. urbano)
        query = query.filter(localidad__icontains=localidad)
        
    padrones = query.all()
    
    if not padrones.exists():
        return Response({'error': 'No se encontró ningún padrón con esos criterios'}, status=404)
        
    # Devolver lista (por si hay más de uno, aunque debería ser único por tipo/localidad)
    data = []
    for p in padrones:
        data.append({
            'id': p.id,
            'numero_padron': p.numero_padron,
            'tipo': p.tipo_padron.nombre if p.tipo_padron else 'Desconocido',
            'localidad': p.localidad,
            'seccion_catastral': p.seccion_catastral,
            'area': p.area_formateada,
            'valor_catastral': p.valor_catastral_real
        })
        
    return Response({'padrones': data})
