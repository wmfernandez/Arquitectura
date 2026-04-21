import os
import re

def modify_settings(filepath, db_suffix):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "import os\nfrom pathlib import Path" not in content:
        content = content.replace("from pathlib import Path", "import os\nfrom pathlib import Path")
    
    if db_suffix == "PADRONES":
        content = re.sub(r"'NAME': 'padrones_db',", f"'NAME': os.getenv('POSTGRES_DB_PADRONES', 'padrones_db'),", content)
        content = re.sub(r"'USER': 'admin_padrones',", f"'USER': os.getenv('POSTGRES_USER_PADRONES', 'admin_padrones'),", content)
        content = re.sub(r"'PASSWORD': 'secret_padrones',", f"'PASSWORD': os.getenv('POSTGRES_PASSWORD_PADRONES', 'secret_padrones'),", content)
        content = re.sub(r"'HOST': 'db_padrones',", f"'HOST': os.getenv('POSTGRES_HOST_PADRONES', 'db_padrones'),", content)
        content = re.sub(r"'PORT': '5432',", f"'PORT': os.getenv('POSTGRES_PORT_PADRONES', '5432'),", content)
    elif db_suffix == "EXPEDIENTES":
        content = re.sub(r"'NAME': 'expedientes_db',", f"'NAME': os.getenv('POSTGRES_DB_EXPEDIENTES', 'expedientes_db'),", content)
        content = re.sub(r"'USER': 'admin_expedientes',", f"'USER': os.getenv('POSTGRES_USER_EXPEDIENTES', 'admin_expedientes'),", content)
        content = re.sub(r"'PASSWORD': 'secret_expedientes',", f"'PASSWORD': os.getenv('POSTGRES_PASSWORD_EXPEDIENTES', 'secret_expedientes'),", content)
        content = re.sub(r"'HOST': 'db_expedientes',", f"'HOST': os.getenv('POSTGRES_HOST_EXPEDIENTES', 'db_expedientes'),", content)
        content = re.sub(r"'PORT': '5432',", f"'PORT': os.getenv('POSTGRES_PORT_EXPEDIENTES', '5432'),", content)
        
        # Secret key, debug, allowed hosts for expedientes
        content = re.sub(r"SECRET_KEY = '.*?'", "SECRET_KEY = os.getenv('DJANGO_SECRET_KEY_EXPEDIENTES', 'django-insecure-expedientes-key')", content)
        content = content.replace("DEBUG = True", "DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'")
        content = content.replace("ALLOWED_HOSTS = ['*']", "ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')")
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    modify_settings("sistema_padrones/sistema_padrones/settings.py", "PADRONES")
    modify_settings("sistema_expedientes/sistema_expedientes/settings.py", "EXPEDIENTES")
    
    # Modify API_EXPEDIENTES_URL in territorio/models.py
    model_path = "sistema_padrones/territorio/models.py"
    with open(model_path, 'r', encoding='utf-8') as f:
        model_content = f.read()
    
    if "from django.conf import settings" not in model_content:
        model_content = "from django.conf import settings\n" + model_content
        
    model_content = model_content.replace("'http://api_expedientes:8000/api/recibir-solicitud/'", "getattr(settings, 'API_EXPEDIENTES_URL', 'http://api_expedientes:8000/api/recibir-solicitud/')")
    
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write(model_content)
        
    # add API_EXPEDIENTES_URL to padrones settings
    padrones_settings = "sistema_padrones/sistema_padrones/settings.py"
    with open(padrones_settings, 'a', encoding='utf-8') as f:
        f.write("\nAPI_EXPEDIENTES_URL = os.getenv('API_EXPEDIENTES_URL', 'http://api_expedientes:8000/api/recibir-solicitud/')\n")
