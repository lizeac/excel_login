from home.models import LoginRecord
from django.db.models import Count
import datetime
from collections import Counter
import matplotlib
matplotlib.use('Agg')
from django.db.models.functions import ExtractWeekDay, ExtractMonth, ExtractYear, ExtractHour
import os
from home.constants import TRANSLATOR, HORARIO_BIBLIOTECA, DIAS_ORDENADOS
import math


def traduzir_ordenar(dicionario):
    '''recebe um dicionário de dias da semana e o organiza
    '''
    
    for dia in list(dicionario.keys()):
        novo_dia = TRANSLATOR.get(dia, dia)
        dicionario[novo_dia] = dicionario.pop(dia)
    ordenado = {dia: dicionario.get(dia, 0) for dia in DIAS_ORDENADOS}
    return ordenado

def consultar_ocorrencias_periodo(ano=None, mes=None):  
    if ano in (None, '', 'none'):
        ano = 'todos'
    if mes in (None, '', 'none'):
        mes = 'todos' 
    """
    mes: número do mês (ex: 9 para setembro). Em caso de None retorna todos 12 meses do ano.
    anos: caso seja None retornará dias da semana de todos os anos em q há registro no banco de dados
    retorna: retorna ocorrencia de dias da semana dentro de determinado periodo
    """

    dias_da_semana = []
    anos_disponiveis = []
    range_dias = range(1, 32)
    mes_atual = datetime.date.today().month
    ano_atual = datetime.date.today().year
    print(f'Foi solicitado fornecer dados referentes a: {ano}, {mes}')
    if ano and ano != 'todos':
        print('entra aqui no ano and ano nao todos')
        try:
            print('Ano existe, entao o ano será', anos_disponiveis)
            ano = int(ano)
            anos_disponiveis.append(ano)
            print(type(ano))
        except:
            print('alguma porcaria aqui')
    else:
        anos_disponiveis = list((LoginRecord.objects.annotate(ano=ExtractYear('data_acesso')).values_list('ano', flat=True).distinct().order_by('ano')))
        print('Ano nao existe especifico, logo, anos serão: ', anos_disponiveis)

    for ano_especifico in anos_disponiveis:
        if ano_especifico == ano_atual:
            range_mes = range(1, mes_atual+1)
        else:
            range_mes = range(1, 13)
        for dia in range_dias:
            if mes:
                try:
                    data = datetime.date(ano_especifico, mes, dia)
                    dias_da_semana.append(data.strftime('%A'))
                except ValueError:
                    print(f"\033[91mErro na Data: {dia} / {mes} /{ano_especifico}\033[0m")
                    continue
            else:
                # Se não tiver mês, gera todas as datas do ano (1 mês de cada)
                print('Nao tem mes, entao cai aqui')
                for m in range_mes:
                    try:
                        data = datetime.date(ano_especifico, m, dia)
                        dias_da_semana.append(data.strftime('%A'))
                    except ValueError:
                        print(f"\033[91mErro na Data: {dia}/{m}/{ano_especifico}\033[0m")
                        continue  # pula dias inválidos como 30/02
    contador = Counter(dias_da_semana)
    contador_ordenado = traduzir_ordenar(contador)

    for x, v in contador_ordenado.items():
        print(f'{x}: {v}')
        print()
    return dict(contador_ordenado)

# --------------------------------------------------------------------------------------------------------------------------
def filtro_de_periodo(ano=None, mes=None):
    print("[DEBUG] filtro_de_periodo foi chamada")
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
def gerar_media_dia(dicionario, ocorrencias):
    '''Gera uma média entre valores de dois dicionarios. O primeiro sao dados do banco de dados, o segundo sao dados reais do periodo'''
    media_ponderada = {}
    for dia in dicionario:
        total = dicionario[dia]
        ocorrencia = ocorrencias.get(dia, 0)
        if ocorrencia:
            media = round(total/ocorrencia, 2)
        else:
            media = 0
        media_ponderada[dia] = media
    return media_ponderada
# ----------------------------------------------------------------------------------------------------

def print_dados_resultados(dicionario,):
    print('dias da semana: ', dicionario)

    


def contar_ocorrencias(ano=None, mes=None):   
    if ano in (None, '', 'none', 'None'):
        ano = 'todos'
    if mes in (None, '', 'none', 'None'):
        mes = 'todos'
    dias_da_semana = []
    mes_int, ano_int = None, None
    print(f'\033[92mRetornando dados referentes a mês: {mes} e ano: {ano}\033[0m')
    print()
    # 1 IF
    if 'todos' != ano and 'todos' != mes:
        # Se passar significa q temos MES e ANO ESPECIFICOS.
        # Ex: 05/2024
        try:
            # variaveis
            ano_int, mes_int = int(ano), int(mes)

            # filtrar as datas que vao determinar os dias da semana
            data_filtrada = list(LoginRecord.objects.filter(data_acesso__year=ano_int, data_acesso__month=mes_int))
            # adicionar na lista os nomes de dias da semana
            dias_da_semana.extend(i.data_acesso.strftime('%A') for i in data_filtrada)
            contador = dict(Counter(dias_da_semana))
            # traduz e ordena os dados para padronizá-los
            contador_ordenado = traduzir_ordenar(contador)
 
            print_dados_resultados(contador_ordenado)
            return contador_ordenado
        except (ValueError, TypeError):
            print(f"[ERRO] Não foi possível converter {ano}, {mes} para inteiro.")
            return {}  
        
        
    # ---------------------------------------------------------------------------------------------------------
    # 1 ELIF
    elif  'todos' == ano and 'todos' != mes:
        # aqui temos o caso do ano TODOS  e mes ESPECIFICO.
        # Exemplo: mes 01 de 2024, 2025
        try:
            mes_int = int(mes)
            # Extrai os dados do banco sobre as datas
            data_filtrada = list(LoginRecord.objects.filter(data_acesso__month=mes_int)) 
            # Transforma esses dados em dia da semana
            dias_da_semana.extend(i.data_acesso.strftime('%A') for i in data_filtrada)
            contador_ordenado = dict(Counter(dias_da_semana))
            # Traduz e ordena os dados
            contador_ordenado = traduzir_ordenar(contador_ordenado)
            # Gera media e adiciona os dados ao dicionario de resultados
            print_dados_resultados(contador_ordenado)

            return contador_ordenado

        except (ValueError, TypeError):
            print(f'Nao foi possível converter mes: {mes} para INTEIRO.')

            return {}
     # ---------------------------------------------------------------------------------------------------------
    # 2 ELIF
    elif 'todos' != ano and 'todos' == mes:
        # Caso ANO seja ESPECIFICO e MES seja TODOS.
        resultados = {}
        try:
            ano_int = int(ano)
            # Extrair dados do banco de dados sobre data
            data_filtrada = list(LoginRecord.objects.filter(data_acesso__year=ano_int)) 
            dias_da_semana.extend(i.data_acesso.strftime('%A') for i in data_filtrada)
            # Conta, traduz e ordena os dados
            contador_ordenado = Counter(dias_da_semana)
            contador_ordenado = traduzir_ordenar(contador_ordenado)
            # Divide as ocorrências uma pela outra pra obter a media
            # Adiciona ao dicionario os dados 
            print_dados_resultados(contador_ordenado)
            print()
            return contador_ordenado
        except (TypeError, ValueError):
            print(f'Nao foi possivel converter ano: {ano} pra inteiro')
            return {}
    # ---------------------------------------------------------------------------------------------------------
    # 3 ELIF
    elif ano in 'todos' and mes in 'todos':
        print(f'\033[94m dentro de elif, Retornando dados referentes a mês: {mes} e ano: {ano}\033[0m')
        # CASO SEJAM TODOS AMBOS ANO E MES
        try:
            data_filtrada = list(LoginRecord.objects.all())
            dias_da_semana.extend(i.data_acesso.strftime('%A') for i in data_filtrada)

            contador_ordenado = Counter(dias_da_semana)
            contador_ordenado = traduzir_ordenar(contador_ordenado)
            print_dados_resultados(contador_ordenado)

            return contador_ordenado
        except (ValueError, TypeError):
            print(f'Exceção ocorrida. no ultimo caso')
            return {}
    
    # ---------------------------------------------------------------------------------------------------------

# Essa classe vai retornar um dicionario contendo todos os dados já filtrados.

class DataExtractor:
    def __init__(self, registros, ano= None, mes=None, output_dir="graficos"):
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
            .values('matricula', 'nome_completo', 'curso') #AQUI PRECISO ADICIONAR ',CURSO' NO FIM, PRA FINS DE TESTE FOI REMOVIDO
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
            .annotate(hora=ExtractHour('hora_acesso')).filter(hora__gte=8, hora__lte=19).values('hora').annotate(total=Count('id')).order_by('hora'))



        # Vai ser necessário pra dividir e gerar a média
        dias_com_acesso = self.registros.values('data_acesso').count()

        # Dict comprehension: gera um valor 0 por chave (hora)
        # Preenche todas as horas com 0, pra garantir que mesmo as horas que não tenham acesso
        # retornem com 0 no dicionário
        medias_hora = {h: 0 for h in HORARIO_BIBLIOTECA}

        for entrada in acesso_por_hora:
            hora = entrada['hora']
            total = entrada['total'] 
            medias_hora[hora] = round(total / dias_com_acesso, 2) if dias_com_acesso else 0
        return medias_hora

    # --------------------------------------------------------------------------------------------------------

        # Gerar gráfico com os dados obtidos logo em seguida
    def gerar_graficos_hora(self, medias_hora):
        import matplotlib.pyplot as plt

        horas = list(medias_hora.keys())
        valores = list(medias_hora.values())

        plt.figure(figsize=(10, 5))
        plt.bar(horas, valores, width=0.6, edgecolor='#004080', color='#66b3ff')

        plt.title("Média de acessos por hora (08h às 19h)", fontsize=14, fontweight='bold', color='#003366')
        plt.xlabel("Hora do dia", fontsize=12)
        plt.ylabel("Média de acessos", fontsize=12)
        plt.xticks(horas)
        plt.grid(axis='y', linestyle='--', alpha=0.4)
        plt.tight_layout()

        path_hora = os.path.join(self.output_dir, f"grafico_media_hora_{self.mes}_{self.ano}.png")
        plt.savefig(path_hora, dpi=120)
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


    def gerar_grafico_semana(self, valores_media_semana):
        import matplotlib.pyplot as plt

        dias = DIAS_ORDENADOS
        valores = valores_media_semana

        plt.figure(figsize=(10, 5))
        plt.bar(dias, valores, color='#99ccff', edgecolor='#004080', width=0.6)

        plt.title("Média de acessos por dia da semana", fontsize=14, fontweight='bold', color='#003366')
        plt.xlabel("Dia da semana", fontsize=12)
        plt.ylabel("Média de acessos", fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.4)
        plt.tight_layout()

        path_dia = os.path.join(self.output_dir, f"grafico_media_dia_semana_{self.mes}_{self.ano}.png")
        plt.savefig(path_dia, dpi=120)
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
        return f''' Dados gerais: {self.calcular_totais()},
        User(s) mais Assíduo(s): {self.aluno_mais_frequente()},
        Curso com mais visitantes: {self.curso_mais_assiduo()},
        Serviço mais utilizado: {self.servico_mais_utilizado()},
        Dia da semana em média com mais fluxo: {self.max_dia_semana()},
        Média de todos os dias da semana: {self.media_dia_semana()},
        Média das Horas: {self.calcular_media_por_hora()}



        '''

