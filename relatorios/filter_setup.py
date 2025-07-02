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


def dias_semana_todos_anos_um_mes(mes):   
    """
    mes: número do mês (ex: 9 para setembro)
    anos: lista de anos (ex: [2024, 2025])
    retorna: dicionário com dias da semana em inglês como chaves e total de ocorrências
    """
    anos_disponiveis = list((
    LoginRecord.objects
    .annotate(ano=ExtractYear('data_acesso'))
    .values_list('ano', flat=True)
    .distinct()
    .order_by('ano')
))
    contador = Counter()
    for ano in anos_disponiveis:
        for dia in range(1, 32):  # de 1 a 31, o máximo possível
            try:
                data = datetime.date(ano, mes, dia)
                dia_semana = data.strftime('%A')  # ex: 'Friday'
                contador[dia_semana] += 1
            except ValueError:
                # Ignora datas inválidas como 31 de setembro
                continue
    contador_pt = {TRANSLATOR.get(k, k): v for k, v in contador_ordenado.items()}
    contador_ordenado = {dia: contador_pt.get(dia, 0) for dia in DIAS_ORDENADOS}
    return dict(contador_ordenado)


def dias_semana_todos():
    anos_disponiveis = list((
    LoginRecord.objects
    .annotate(ano=ExtractYear('data_acesso'))
    .values_list('ano', flat=True)
    .distinct()
    .order_by('ano')
))
    mes_atual = datetime.date.today().month
    ano_atual = datetime.date.today().year
    contador = Counter()
    for ano in anos_disponiveis:
        if ano != ano_atual:
            meses = range(1, 13)
        else:
            meses = range(1, mes_atual+1)
        for mes in meses:
            for dia in range(1, 32):  # de 1 a 31, o máximo possível
                try:
                    data = datetime.date(ano, mes, dia)
                    dia_semana = data.strftime('%A')  # ex: 'Friday'
                    contador[dia_semana] += 1
                except ValueError:
                    # Ignora datas inválidas como 31 de setembro
                    continue
    contador_pt = {TRANSLATOR.get(k, k): v for k, v in contador.items()}
    contador_ordenado = {dia: contador_pt.get(dia, 0) for dia in DIAS_ORDENADOS}
    return dict(contador_ordenado)


# retorna um queryset seja um mensal ou um anual
def ocorrencias_dias_semana(ano, mes=None):
    dias_da_semana = []
    range_dias = range(1, 32)

    for dia in range_dias:
        try:
            if mes:
                data = datetime.date(ano, mes, dia)
            else:

                # Se não tiver mês, gera todas as datas do ano (1 mês de cada)
                for m in range(1, 13):
                    data = datetime.date(ano, m, dia)
                    dias_da_semana.append(data.strftime('%A'))
                continue
            dias_da_semana.append(data.strftime('%A'))
        except ValueError:
            continue  # pula dias inválidos como 30/02
    dias_contados = dict(Counter(dias_da_semana))    
    dias_da_semana_pt = {TRANSLATOR.get(k, k): v for k, v in dias_contados.items()}
    contador_ordenado = {dia: dias_da_semana_pt.get(dia, 0) for dia in DIAS_ORDENADOS}

    return dict(Counter(contador_ordenado))

def contar_e_traduzir(lista):
    dicionario = dict(Counter(lista))
    '''Pra gerar uma lista grande com todos os dias da semana do historico do banco de dados'''
    for dia in list(dicionario.keys()):
        novo_dia = TRANSLATOR.get(dia, dia)
        dicionario[novo_dia] = dicionario.pop(dia)
    return dicionario

def filtro_de_periodo(ano=None, mes=None):
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

def contar_ocorrencias(ano=None, mes=None):
    anos_disponiveis = list((
    LoginRecord.objects.annotate(ano=ExtractYear('data_acesso')).values_list('ano', flat=True).distinct().order_by('ano')))
        
    dias_da_semana = []
    filtro_dias_semana = {}
    mes_int, ano_int = None, None
    print(f'Retornando dados referentes a mês: {mes} e ano: {ano}')
    print()

    if 'todos' != ano and 'todos' != mes:
        # Se passar significa q temos MES e ANO ESPECIFICOS.
        # Ex: 05/2024
        try:
            # variaveis
            resultados = {}
            ano_int, mes_int = int(ano), int(mes)
            contador_ocorrencias = ocorrencias_dias_semana(ano_int, mes_int)
            ocorrencia_ordenada = {dia: contador_ocorrencias.get(dia, 0) for dia in DIAS_ORDENADOS}
            media_ponderada = {}

            # filtrar as datas que vao determinar os dias da semana
            data_filtrada = list(LoginRecord.objects.filter(data_acesso__year=ano_int, data_acesso__month=mes_int))
            # adicionar na lista os nomes de dias da semana
            dias_da_semana.extend(i.data_acesso.strftime('%A') for i in data_filtrada)
            filtro_dias_semana = contar_e_traduzir(dias_da_semana)
            contador_ordenado = {dia: filtro_dias_semana.get(dia, 0) for dia in DIAS_ORDENADOS}
            resultados['dias_semana'] = contador_ordenado

            # gerar a media correspondente a este periodo

            for dia in contador_ordenado:
                total = contador_ordenado[dia]
                ocorrencia = ocorrencia_ordenada.get(dia, 0)
                if ocorrencia:
                    media = round(total/ocorrencia, 2)
                else:
                    media = 0
                media_ponderada[dia] = media
            resultados['media'] = media_ponderada
            print('dias da semana: ', resultados['dias_semana'])
            print('ocorrencias no periodo:' , ocorrencia_ordenada)
            print('medias: ', resultados['media'])
    
            return resultados
        except (ValueError, TypeError):
            print(f"[ERRO] Não foi possível converter ano/mes: {ano}, {mes} para inteiro.")
            return {}  
        
        
    # ---------------------------------------------------------------------------------------------------------

    elif  'todos' == ano and 'todos' != mes:
        # aqui temos o caso do ano TODOS  e mes ESPECIFICO.
        registros_periodo = LoginRecord.objects.filter(data_acesso__year__in=anos_disponiveis) #aqui extraimos os registros do periodo solicitado
        resultado = {}
        try:
            mes_int = int(mes)
            contador_ocorrencia = dias_semana_todos_anos_um_mes(mes_int)
            ocorrencia_ordenada = {dia: contador_ocorrencia.get(dia, 0) for dia in DIAS_ORDENADOS}
            data_filtrada = list(LoginRecord.objects.filter(data_acesso__month=mes_int)) 
            dias_da_semana.extend(i.data_acesso.strftime('%A') for i in data_filtrada)
            filtro_dias_semana_pt = contar_e_traduzir(dias_da_semana)
            contador_ordenado = {dia: filtro_dias_semana_pt.get(dia, 0) for dia in DIAS_ORDENADOS}
            return filtro_dias_semana
 
        except (ValueError, TypeError):
            print(f'Nao foi possível converter mes: {mes} para INTEIRO.')
            return {}
     # ---------------------------------------------------------------------------------------------------------

    elif 'todos' != ano and 'todos' == mes:
        # Caso ANO seja ESPECIFICO e MES seja TODOS.
        resultado = {}
        try:
            ano_int = int(ano)
            ocorrencias = ocorrencias_dias_semana(ano=ano_int)
            data_filtrada = list(LoginRecord.objects.filter(data_acesso__year=ano_int)) 
            dias_da_semana.extend(i.data_acesso.strftime('%A') for i in data_filtrada)
            filtro_dias_semana = contar_e_traduzir(dias_da_semana)

            return filtro_dias_semana 
        except (TypeError, ValueError):
            print(f'Nao foi possivel converter ano: {ano} pra inteiro')
            return {}
    # ---------------------------------------------------------------------------------------------------------
     
    elif 'todos' == ano and 'todos' == mes:
        # CASO SEJAM TODOS AMBOS ANO E MES
        resultado = {}
        try:
            data_filtrada = list(LoginRecord.objects.values_list('data_acesso', flat=True).distinct())
            dias_da_semana.extend(i.strftime('%A') for i in data_filtrada)
            filtro_dias_semana = contar_e_traduzir(dias_da_semana)

            return filtro_dias_semana 
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

        dias_do_mes = contar_ocorrencias(self.ano, self.mes)
        print(  )

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

