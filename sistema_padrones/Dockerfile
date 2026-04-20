FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Agregamos --no-install-recommends para evitar descargar paquetes extras
# y reducir drásticamente el consumo de memoria RAM de Docker al compilar.
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
       binutils \
       libproj-dev \
       gdal-bin \
       libgdal-dev \
       python3-gdal \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./sistema_padrones /app/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
