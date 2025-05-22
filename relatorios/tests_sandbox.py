# inicia o django sem necessidade do runserver, pra fins de teste de codigos
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from django.http import FileResponse
import io
from datetime import datetime
from extractor_data import DataExtractor

import os
import sys
import django

# Adiciona o diretório raiz do projeto ao sys.path
PROJETO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJETO_DIR)

# Configura e inicia o Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "excel_login.settings")
django.setup()

from home.models import LoginRecord


django.setup()

months_name = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
               'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
data_month = datetime.now().strftime('%m')
data_month = int(data_month)
month_name = months_name[data_month-1]






extrator = DataExtractor(mes=5)
pessoamais = extrator.gerar_dados()
