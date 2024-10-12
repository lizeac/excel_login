from django.db.models import Count
from datetime import datetime
from .models import LoginRecord
dates = datetime.now().hour
month = dates.strftime('%m/%Y')
# Consultar o visitante mais frequente do mês
visitante_mais_frequente = LoginRecord.objects.filter(
    visitante='Visitante', 
    data_acesso__month=month
).values('matricula', 'nome_completo').annotate(
    total_acessos=Count('id')
).order_by('-total_acessos').first()


