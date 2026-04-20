import json
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from territorio.models import Padron, TipoPadron

class Command(BaseCommand):
    help = 'Carga padrones desde un archivo GeoJSON'

    def add_arguments(self, parser):
        parser.add_argument('filepath', type=str, help='Ruta al archivo .geojson dentro del contenedor')
        parser.add_argument('tipo_padron', type=str, help='Tipo de padrón (Ej: Urbano o Rural)')

    def handle(self, *args, **kwargs):
        filepath = kwargs['filepath']
        tipo_str = kwargs['tipo_padron']

        # Aseguramos que el tipo exista
        tipo_padron, _ = TipoPadron.objects.get_or_create(nombre=tipo_str)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al leer el archivo: {e}"))
            return

        features = data.get('features', [])
        self.stdout.write(f"Iniciando carga de {len(features)} padrones ({tipo_str})...")

        # Limpiamos los padrones anteriores de este tipo para evitar duplicados en recargas
        self.stdout.write("Borrando registros anteriores de este tipo...")
        Padron.objects.filter(tipo_padron=tipo_padron).delete()

        count = 0
        errores = 0

        # Para cargas masivas rápidas
        batch = []

        for feat in features:
            props = feat.get('properties', {})
            geom_dict = feat.get('geometry')
            
            num_padron = str(props.get('PADRON', ''))
            
            if not num_padron or num_padron == '0' or num_padron == 'None':
                continue
                
            depto = props.get('NOMDEPTO', '')
            loccat = props.get('NOMLOCCAT', '')
            
            geom = None
            if geom_dict:
                try:
                    geom = GEOSGeometry(json.dumps(geom_dict))
                except Exception as e:
                    pass

            batch.append(Padron(
                numero_padron=num_padron,
                tipo_padron=tipo_padron,
                geometria=geom,
                departamento=depto,
                localidad=loccat,
                atributos_gis=props
            ))

            count += 1
            if len(batch) >= 2000:
                Padron.objects.bulk_create(batch)
                batch = []
                self.stdout.write(f"Cargados {count} padrones...")

        # Guardar los restantes
        if batch:
            Padron.objects.bulk_create(batch)

        self.stdout.write(self.style.SUCCESS(f"Éxito: Se procesaron y guardaron {count} padrones {tipo_str}."))
