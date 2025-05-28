from home.models import LoginRecord
from django.db.models import Count
from django.db.models.functions import ExtractHour
import datetime
from collections import Counter
import matplotlib.pyplot as plt
import os


# função primordial para a execução da classe a seguir, recebe a condição de filtro necessaria
def filter_of_period(ano, mes=None):
    if mes and mes != "todos":
        mes = int(mes)
        return LoginRecord.objects.filter(data_acesso__month=mes, data_acesso__year=ano)

    return LoginRecord.objects.filter(data_acesso__year=ano)



def contar_ocorrencias_dias(mes, ano):
    dias = []
    # se o usuário escolher algum mes especificos e nao "todos" (relatório mensal)
    if mes:
        range_dias = range(1, 32)
        meses = [mes]
    else:
        # relatorio anual
        range_dias = range(1, 32)
        meses = range(1, 13)

    for m in meses:
        for dia in range_dias:
            try:
                data = datetime.date(ano, m, dia)
                dias.append(data.strftime('%A'))
            except ValueError:
                continue

    tradutor = {
        'Monday': 'Segunda-feira',
        'Tuesday': 'Terça-feira',
        'Wednesday': 'Quarta-feira',
        'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo',
    }

    dias_traduzidos = [tradutor[d] for d in dias]
    return dict(Counter(dias_traduzidos))


# Essa classe vai retornar um dicionario contendo todos os dados já filtrados.

class DataExtractor:
    def __init__(self, registros, mes=None, output_dir="graficos"):
        self.registros = registros
        self.mes = mes
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.resultado = {}
 

    def calcular_totais(self):
        # Conta o total de usuários do mês
        self.resultado['total_acessos'] = self.registros.count()

        # total de usuários não-ufba no mês
        self.resultado['total_visitantes'] = self.registros.filter(visitante='Visitante').count()

        # Total de usuários Ufba no mês
        self.resultado['total_usuarios_ufba'] = self.registros.filter(visitante='Usuário UFBA').count()

    def aluno_mais_frequente(self):
        # Retorna um queryset com os dados solicitados,
        # conta os usuários de acordo com ids únicos
        mais_frequente = (
            self.registros
            .values('matricula', 'nome_completo') #AQUI PRECISO ADICIONAR ',CURSO' NO FIM, PRA FINS DE TESTE FOI REMOVIDO
            .annotate(total=Count('id'))
            .order_by('-total')
            .first()
        )


# caso de empate, adicionar
        if mais_frequente:
            self.resultado['aluno_mais_frequente'] = {
                mais_frequente['nome_completo']: {
                    "matricula": mais_frequente['matricula'],
                    "curso": mais_frequente['curso'],
                    "total_de_visitas": mais_frequente['total']
                }
            }
        else:
            self.resultado['aluno_mais_frequente'] = {}

    def curso_mais_assiduo(self):
        # Qual curso que mais teve alunos frequentes
        curso = (
            self.registros
            .values('curso')
            .annotate(total=Count('id'))
            .order_by('-total')
            .first()
        )
        self.resultado['curso_mais_assiduo'] = curso if curso else {}

    def servico_mais_utilizado(self):
        # Qual serviço que mais foi utilizado
        servico = (
            self.registros
            .values('servico')
            .annotate(total=Count('id'))
            .order_by('-total')
            .first()
        )
        self.resultado['servico_mais_utilizado'] = servico if servico else {}

    def calcular_media_por_hora(self):
        # Anota a hora do campo data_acesso
        # 8 a 19 é o período de funcionamento da biblioteca
        acesso_por_hora = (
            self.registros
            .annotate(hora=ExtractHour('hora_acesso'))
            .filter(hora__gte=8, hora__lte=19)
            .values('hora')
            .annotate(total=Count('id'))
            .order_by('hora')
        )
    

        # Vai ser necessário pra dividir e gerar a média
        dias_com_acesso = self.registros.values('data_acesso').distinct().count()

        # Dict comprehension: gera um valor 0 por chave (hora)
        # Preenche todas as horas com 0, pra garantir que mesmo as horas que não tenham acesso
        # retornem com 0 no dicionário
        medias_por_hora = {h: 0 for h in range(8, 20)}

        for entrada in acesso_por_hora:
            hora = entrada['hora']
            total = entrada['total']
            medias_por_hora[hora] = round(total / dias_com_acesso, 2) if dias_com_acesso else 0

        self.resultado['medias_por_hora'] = medias_por_hora


        # Gerar gráfico com os dados obtidos logo em seguida
        plt.figure(figsize=(10, 5))
        plt.bar(medias_por_hora.keys(), medias_por_hora.values())
        plt.title("Média de acessos por hora (08h às 19h)")
        plt.xlabel("Hora do dia")
        plt.ylabel("Média de acessos")
        plt.xticks(list(medias_por_hora.keys()))
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        path_hora = os.path.join(self.output_dir, f"grafico_media_hora_{self.mes}.png")
        plt.savefig(path_hora)
        plt.close()

        self.resultado['grafico_hora'] = path_hora

    # Pra quando adicionar a coluna dia da semana ao banco de dados:
    def dia_semana_mais_frequente(self):

    # Agrupa por dia_da_semana e conta os acessos
        por_dia = (
        self.registros
        .values('dia_da_semana')
        .annotate(total=Count('id'))
    )

        # Conta quantas vezes cada dia da semana aparece no mês
        ano = datetime.date.today().year  #Da pra colocar o ano como um input pra adaptar depois
        dias_do_mes = contar_ocorrencias_dias(self.mes, ano)

        # Calcula média por ocorrência
        medias = {}
        for entrada in por_dia:
            dia = entrada['dia_da_semana']
            total = entrada['total']
            ocorrencias = dias_do_mes.get(dia, 0)
            media = round(total / ocorrencias, 2) if ocorrencias else 0
            medias[dia] = media

        self.resultado['media_por_dia_semana'] = medias

            # Gerar gráfico
        dias_ordenados = ["Segunda-feira", "Terça-Feira", "Quarta-Feira", "Quinta-feira", "Sexta-Feira", "Sabado"]
        valores = [medias.get(d, 0) for d in dias_ordenados]

        plt.figure(figsize=(10, 5))
        plt.bar(dias_ordenados, valores)
        plt.title("Média de acessos por dia da semana")
        plt.xlabel("Dia da semana")
        plt.ylabel("Média de acessos")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        path_dia = os.path.join(self.output_dir, f"graf_media_dia_semana_{self.mes}.png")
        plt.savefig(path_dia)
        plt.close()

        self.resultado['grafico_dia_semana'] = path_dia

    def gerar_dados(self):
        self.calcular_totais()
        self.aluno_mais_frequente()
        self.curso_mais_assiduo()
        self.servico_mais_utilizado()
        self.calcular_media_por_hora()
        self.dia_semana_mais_frequente()
        return self.resultado

