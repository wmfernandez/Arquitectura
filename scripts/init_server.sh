#!/bin/bash

# Asegurarse de que el script se detenga si hay un error crítico
set -e

echo "🚀 Iniciando configuración del nuevo servidor para Arquitectura..."

# 1. Levantar los contenedores en segundo plano
echo "📦 Levantando contenedores de Docker..."
docker compose up -d

echo "⏳ Esperando 10 segundos para que las bases de datos (PostgreSQL/PostGIS) estén completamente listas..."
sleep 10

# 2. Ejecutar migraciones
echo "🛠️ Ejecutando migraciones de la base de datos de Padrones..."
docker compose exec api_padrones python manage.py migrate

echo "🛠️ Ejecutando migraciones de la base de datos de Expedientes..."
docker compose exec api_expedientes python manage.py migrate

# 3. Cargar datos geográficos (GeoJSON)
echo "🗺️ Comprobando si existen archivos GeoJSON para cargar datos espaciales..."

# Evaluamos dentro del contenedor si existe el archivo para evitar errores
docker compose exec api_padrones sh -c '
if [ -f "rural.geojson" ]; then
    echo "Cargando padrones rurales..."
    python manage.py load_geojson rural.geojson rural
else
    echo "⚠️ Archivo rural.geojson no encontrado, saltando paso."
fi

if [ -f "urbano.geojson" ]; then
    echo "Cargando padrones urbanos..."
    python manage.py load_geojson urbano.geojson urbano
else
    echo "⚠️ Archivo urbano.geojson no encontrado, saltando paso."
fi
'

# 4. Crear superusuario
echo "👤 Creando superusuario administrador. Sigue las instrucciones en pantalla:"
docker compose exec api_padrones python manage.py createsuperuser

echo "✅ ¡Configuración finalizada con éxito!"
echo "➡️ Puedes acceder al panel de administración en http://<IP_DEL_SERVIDOR>:8000/admin"
echo "➡️ El portal de profesionales está corriendo en http://<IP_DEL_SERVIDOR>:5173"
