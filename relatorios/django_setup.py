import os
import sys
import django

# Caminho absoluto até o diretório onde está o manage.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Nome do módulo de settings (ajuste se for diferente!)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "excel_login.settings")

# Inicializa o Django
django.setup()