import os
from django.db.models import Count
from django.db.models.functions import ExtractHour


# função primordial para a execução da classe a seguir, recebe a condição de filtro necessaria
def filter_of_period(ano, mes=None):
    if mes and mes != "todos":
        mes = int(mes)
        registros = LoginRecord.objects.filter(data_acesso__month=mes, data_acesso__year=ano)
    else:
        registros = LoginRecord.objects.filter(data_acesso__year=ano)
    return registros



class DataExtractor:
    def __init__(self, registros, output_dir="graficos"):
        """
        registros: queryset de LoginRecord já filtrado (por mês, ano, etc.)
        output_dir: pasta onde os gráficos serão salvos (opcional)
        """
        self.registros = registros
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.resultado = {}

    def total_acessos(self):
        return self.registros.count()

    def total_visitantes(self):
        return self.registros.values('matricula').distinct().count()

    def curso_mais_assiduo(self):
        return self.registros.values('curso') \
            .annotate(total=Count('curso')) \
            .order_by('-total') \
            .first()

    def servico_mais_utilizado(self):
        return self.registros.values('servico') \
            .annotate(total=Count('servico')) \
            .order_by('-total') \
            .first()

    def horas_mais_movimentadas(self):
        return self.registros \
            .annotate(hora=ExtractHour('hora_acesso')) \
            .values('hora') \
            .annotate(total=Count('id')) \
            .order_by('-total')

    def dias_mais_movimentados(self):
        return self.registros.values('dia_da_semana') \
            .annotate(total=Count('id')) \
            .order_by('-total')
