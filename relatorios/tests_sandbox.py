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



from relatorios.filter_setup import DataExtractor, filter_of_period
from pprint import pprint

from home.models import LoginRecord
from django.db.models import Count
from datetime import datetime

registros = filter_of_period(ano=2025, mes=6)
data = DataExtractor(registros=registros, mes=6, ano=2025)
print(data.mostrar_dados_gerais())

