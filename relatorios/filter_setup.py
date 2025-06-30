from home.models import LoginRecord
from django.db.models import Count
import datetime
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.db.models.functions import ExtractWeekDay, ExtractMonth, ExtractYear, ExtractHour
import os
from home.constants import TRANSLATOR, HORARIO_BIBLIOTECA, DIAS_ORDENADOS
import math




# função primordial para a execução da classe a seguir, recebe a condição de filtro necessaria
# retorna um queryset seja um mensal ou um anual
def filter_of_period(ano=None, mes=None):
    '''Queryset: Filtra o periodo do ano de acordo com o inserido, sejam dados mensais ou anuais
    '''
    try:
        # tentar converter o ano pra número inteiro
        ano_int = int(ano)
    except (ValueError, TypeError):
        # vai entrar aqui caso o valor do ano seja 'todos'
        print('Não foi possível converter a o input para número inteiro, ano selecionado será "todos".')
        ano_int = None
    try:
        mes_int = int(mes)
    
    except (ValueError, TypeError):
        # tentar converter o mes pra numero inteiro
        mes_int = None
        print('Não foi possível converter o mês para inteiro, ele será considerado: Todos')

    f_registro = LoginRecord.objects.all()
    if ano_int:
        if mes_int:
            # ou seja, se o filtro for mensal e específico
            f_registro = f_registro.filter(data_acesso__year=ano_int,
                                data_acesso__month = mes_int)
        else:
            # ou seja, vai mostrar todos os meses do ano selecionado
            f_registro = f_registro.filter(data_acesso__year=ano_int)
            
        
    # aqui pra mostrar resultados de todos os anos 
    else:
        # em caso de todos os anos
        if mes_int:
            f_registro = f_registro.filter(data_acesso__month = int(mes))

    if f_registro:
        f_registro = f_registro.order_by('-data_acesso')
    return {'queryset':f_registro,
            'mes': mes_int,  
            'ano': ano_int,            
            }

#---------------------------------------------------------------------------------------------------------------------------

def contar_ocorrencias_dias(mes, ano):

    if mes != 'todos':
        mes = int(mes)
    if ano != 'todos':
        ano = int(ano)
    '''Dict: Conta quantas vezes cada dia da semana houveram no periodo selecionado'''
    dias = []
    # se o usuário escolher algum mes especificos e nao "todos" (relatório mensal)
    if mes and mes !='todos':
        print('relatorio mensal')
        range_dias = range(1, 32)
        meses = [mes]

        for m in meses:
            for dia in range_dias:
                try:
                    # por algum motivo essa linha aqui abaixo ta dando erro
                    # os valores estao sendo recebidos errados e eu nao sei dizer o porque.
                    data = datetime.date(m, ano, dia)
                    dias.append(data.strftime('%A'))
                except (ValueError, TypeError):
                    continue
        
# dfdfd
    else:
        print('relatorio anual')
        # relatorio anual
        range_dias = range(1, 32)
        meses = range(1, 13)
    
        anos = (
            LoginRecord.objects
            .annotate(ano=ExtractYear('data_acesso'))
            .values_list('ano', flat=True)
            .distinct()
        )

        # print(list(anos))


    # for m in meses:
    #     for dia in range_dias:
    #         try:
    #             # por algum motivo essa linha aqui abaixo ta dando erro
    #             # os valores estao sendo recebidos errados e eu nao sei dizer o porque.
    #             data = datetime.date(m, ano, dia)
    #             dias.append(data.strftime('%A'))
    #         except (ValueError, TypeError):
    #             continue
        
        

    tradutor = TRANSLATOR
    dias_traduzidos = [tradutor[d] for d in dias]
    # counter retorna a contagem de cada um dos valores da lista. vai armazenar num dicionario
    # sendo o valor do dia a chave e a contagem dele o valor
    for chave, valor in dict(Counter(dias_traduzidos)).items():
        print(f'chave {chave}, valor {valor}.')
    return dict(Counter(dias_traduzidos))


# -------------------------------------------------------------------------------------------------------------------------


# Essa classe vai retornar um dicionario contendo todos os dados já filtrados.

class DataExtractor:
    def __init__(self, registros, mes=None, ano= None, output_dir="graficos"):
        """
        registros: queryset de LoginRecord já filtrado (por mês, ano, etc.)
        output_dir: pasta onde os gráficos serão salvos (opcional)
        """
        self.registros = registros
        if not mes:
            mes = 'todos'
        if not ano:
            ano = 'todos'
        self.mes = mes
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.ano = ano

        self.valores_media_semana = []
 

    def calcular_totais(self):
        '''dict: Retorna o total de acessos no mês, total de visitantes externos e internos(Ufba).'''
        # Conta o total de usuários do periodo solicitado
        total_acessos = self.registros.count()

        # total de usuários não-ufba do periodo solicitado
        total_visitantes = self.registros.filter(visitante='Visitante').count()

        # Total de usuários Ufba do periodo solicitado
        total_usuarios_ufba = self.registros.filter(visitante='Usuário UFBA').count()

        return {'total_acessos': total_acessos,
                'total_visitantes': total_visitantes,
                'total_usuario_ufba': total_usuarios_ufba}
    
    # ----------------------------------------------------------------------------------

    def aluno_mais_frequente(self):
        # Retorna uma lista contendo dicionarios com dados dos que tiveram maior frequencia
        # porque existe a possibilidade de ser mais de um usuario com o mesmo numero 1 de frequencias
        # conta o id de cada aluno com base na matricula
        mais_frequente = (
            self.registros
            .values('matricula', 'nome_completo') #AQUI PRECISO ADICIONAR ',CURSO' NO FIM, PRA FINS DE TESTE FOI REMOVIDO
            .annotate(total=Count('id'))
            .order_by('-total', 'nome_completo')

        )

        if mais_frequente:
            max_total = mais_frequente[0]['total']
            todos_mais_frequentes = [aluno for aluno in mais_frequente if aluno['total'] == max_total]
            return todos_mais_frequentes
        
        return []

    # ---------------------------------------------------------------------------------------------------------------

    def curso_mais_assiduo(self):
        # Qual curso que mais teve alunos frequentes
        curso = (
            self.registros
            .values('curso')
            .annotate(total=Count('id'))
            .order_by('-total')
            .first()
        )
        if curso:
            return curso
        return {}

    # -------------------------------------------------------------------------------------------------------------

    def servico_mais_utilizado(self):
        # Qual serviço que mais foi utilizado
        servico = (
            self.registros
            .values('servico')
            .annotate(total=Count('id'))
            .order_by('-total')
            .first()
        )
        if servico:
            return servico
        return {}

    # -------------------------------------------------------------------------------------------------------------

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
        medias_hora = {h: 0 for h in HORARIO_BIBLIOTECA}

        for entrada in acesso_por_hora:
            hora = entrada['hora']
            total = entrada['total'] 
            medias_hora[hora] = math.ceil(total / dias_com_acesso) if dias_com_acesso else 0
        return medias_hora

    # --------------------------------------------------------------------------------------------------------

        # Gerar gráfico com os dados obtidos logo em seguida
    def gerar_graficos_hora(self, medias_hora):
        plt.figure(figsize=(10, 5))
        plt.bar(medias_hora.keys(), medias_hora.values())
        plt.title("Média de acessos por hora (08h às 19h)")
        plt.xlabel("Hora do dia")
        plt.ylabel("Média de acessos")
        plt.xticks(list(medias_hora.keys()))
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        path_hora = os.path.join(self.output_dir, f"grafico_media_hora_{self.mes}_{self.ano}.png")
        caminho_completo = os.path.join(self.output_dir, path_hora)
        plt.savefig(caminho_completo)
        plt.close()

        return path_hora

    # ------------------------------------------------------------------------------------------------------------------

    def max_dia_semana(self):
        dia_semana = (
        self.registros
        .values('dia_da_semana')
        .annotate(total=Count('id')).
        order_by('-total').
        first()
    )
        return dia_semana

    # -----------------------------------------------------------------------------------------------------------------

    def media_dia_semana(self):
        por_dia = (
            self.registros
            .values('dia_da_semana')
            .annotate(total=Count('id'))
        )

        dias_do_mes = contar_ocorrencias_dias(self.mes, self.ano)
        for chave, valor in dias_do_mes.items():
            print(chave, valor)
        medias = {}
        for item in por_dia:
            dia_en = item['dia_da_semana']
            total = item['total']
            # dia_pt = TRANSLATOR.get(dia_en, 'Desconhecido')
            ocorrencias = dias_do_mes.get(dia_en, 0)
            media = round(total / ocorrencias, 2) if ocorrencias else 0
            media = media 
            medias[dia_en] = media

        valores_media_semana = [medias.get(d, 0) for d in DIAS_ORDENADOS]

        return valores_media_semana

    # -----------------------------------------------------------------------------------------------------------------

    def gerar_grafico_semana(self, valores_media_semana):
        plt.figure(figsize=(10, 5))
        plt.bar(DIAS_ORDENADOS, valores_media_semana)
        plt.title("Média de acessos por dia da semana")
        plt.xlabel("Dia da semana")
        plt.ylabel("Média de acessos")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        path_dia = os.path.join(self.output_dir, f"graf_media_dia_semana_{self.mes}_{self.ano}.png")
        caminho_completo = os.path.join(self.output_dir, path_dia)
        plt.savefig(caminho_completo)
        plt.close()

        return path_dia
        
    # ----------------------------------------------------------------------------------------------------------------------

    def gerar_dados(self):
        resultado = dict()
        media_semana = self.media_dia_semana()
        media_horas = self.calcular_media_por_hora()
        resultado['Totais'] = self.calcular_totais()
        resultado['AlunoMaisFrequente'] = self.aluno_mais_frequente()
        resultado['CursoMaisFrequente'] = self.curso_mais_assiduo()
        resultado['ServicoMaisFrequente'] = self.servico_mais_utilizado()
        print('gerando grafico Hora...')
        self.gerar_graficos_hora(media_horas)
        print('gerando grafico Semana...')
        self.gerar_grafico_semana(media_semana)

        return resultado

    # ----------------------------------------------------------------------------------------------------------------------

    def mostrar_dados_gerais(self):
        media_semana = self.media_dia_semana()
        media_horas = self.calcular_media_por_hora()


        return f''' Dados gerais: {self.calcular_totais()},
        User(s) mais Assíduo(s): {self.aluno_mais_frequente()},
        Curso com mais visitantes: {self.curso_mais_assiduo()},
        Serviço mais utilizado: {self.servico_mais_utilizado()},
        Dia da semana em média com mais fluxo: {self.max_dia_semana()},
        Média de todos os dias da semana: {self.media_dia_semana()},
        Média das Horas: {self.calcular_media_por_hora()}



        '''

