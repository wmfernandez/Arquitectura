# Scripts de Inicialización del Servidor

Esta carpeta contiene scripts de utilidad para hacer más sencillo el despliegue del proyecto en servidores nuevos (como Ubuntu).

## `init_server.sh`

Este script automatiza los primeros pasos luego de clonar el proyecto en un servidor nuevo. Se encarga de:

1. Levantar todos los contenedores en segundo plano (`docker compose up -d`).
2. Dar un pequeño margen de tiempo a que PostgreSQL arranque correctamente.
3. Ejecutar las migraciones de bases de datos para **Padrones** y **Expedientes**.
4. Cargar automáticamente los datos espaciales (`rural.geojson` y `urbano.geojson`) en la base de datos si es que estos archivos están disponibles.
5. Iniciar el proceso interactivo para crear tu **Superusuario Administrador** de Django.

### Cómo usarlo en tu servidor Ubuntu:

1. Ingresa a la carpeta raíz del proyecto:
   ```bash
   cd Arquitectura
   ```

2. Dale permisos de ejecución al script (esto solo se hace una vez):
   ```bash
   chmod +x scripts/init_server.sh
   ```

3. Ejecuta el script:
   ```bash
   ./scripts/init_server.sh
   ```

Simplemente sigue las instrucciones que vayan apareciendo en la consola. Al finalizar, tu sistema estará 100% operativo y poblado con datos base.
