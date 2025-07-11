from django.shortcuts import render
from django.db.models.functions import ExtractYear
from django.contrib.auth.decorators import user_passes_test, login_required
from home.models import LoginRecord
from home.constants import MONTHS, DIAS_ORDENADOS
# importar o banco de dados do que os alunos forneceram
from home.models import LoginRecord
from relatorios.filter_setup import DataExtractor, contar_ocorrencias, filtro_de_periodo
from django.conf import settings
import os
from django.http import FileResponse


from datetime import datetime


imagem_path = 'relatorios/static/brasao_icti.png'
media_dia = []
# só permitir superusers
def superuser_required(user):
    return user.is_superuser
# # Create your views here.
# @login_required(login_url='/admin/login/')
# @user_passes_test(superuser_required)

def dashboard_view(request):
    # pegar os anos existentes do banco de dados para mostrar ao usuário, para poder selecionar na dashboard:
    anos_disponiveis = LoginRecord.objects.annotate(ano=ExtractYear('data_acesso')).values_list('ano', flat=True).distinct()
    ano_selecionado = request.GET.get('ano')
    mes_selecionado = request.GET.get('mes')


    dados_gerais = {}
    usuario_assiduo = []
    curso_frequente = {}
    servico_frequente = {}
    max_dia_semana = {}
    valores_dias_semanas = []
    media_horas = {}
    grafico_hora = ''
    grafico_semana = ''
    grafico_hora_url = None
    grafico_semana_url = None
    valores_ordenados = []

    queryset = {'queryset': [], 'ano': ano_selecionado, 'mes': mes_selecionado}
    
    # if ano_selecionado.strip().lower() == 'none':
    #         ano_selecionado = None
    # if mes_selecionado.strip().lower() == 'none':
    #         mes_selecionado = None



    if ano_selecionado or mes_selecionado:
        queryset = filtro_de_periodo(ano_selecionado, mes_selecionado)
        contador_ocorrencias = contar_ocorrencias(ano_selecionado, mes_selecionado)

        extrator = DataExtractor(queryset.get('queryset', []), 
                                 queryset.get('ano'), queryset.get('mes'), 
                                 output_dir=settings.GRAFICOS_ROOT)

        dados_gerais = extrator.calcular_totais()
        usuario_assiduo = extrator.aluno_mais_frequente()
        curso_frequente = extrator.curso_mais_assiduo()
        servico_frequente = extrator.servico_mais_utilizado()
        max_dia_semana = extrator.max_dia_semana()
        valores_dias_semanas_dict = contador_ocorrencias
        valores_ordenados = [(dia, valores_dias_semanas_dict.get(dia, 0)) for dia in DIAS_ORDENADOS]
        valores_dias_semanas_graf = [valores_dias_semanas_dict.get(dia, 0) for dia in DIAS_ORDENADOS]

        media_horas = extrator.calcular_media_por_hora()
        grafico_hora = extrator.gerar_graficos_hora(media_horas)
        grafico_semana = extrator.gerar_grafico_semana(valores_dias_semanas_graf)
        grafico_hora_url = f"{settings.GRAFICOS_URL}{os.path.basename(grafico_hora)}"
        grafico_semana_url = f"{settings.GRAFICOS_URL}{os.path.basename(grafico_semana)}"


    context = {
    'registros': queryset.get('queryset', []),
    'ano_selecionado': queryset.get('ano'),
    'mes_selecionado': queryset.get('mes'),
    'anos_disponiveis': anos_disponiveis,
    'meses_disponiveis': MONTHS,
    'dados_gerais': dados_gerais,
    'usuario_assiduo' : usuario_assiduo,
    'curso_frequente': curso_frequente,
    'servico_frequente':servico_frequente,
    'max_dia_semana': max_dia_semana,
    'total_dias_semanas':valores_ordenados,
    'media_horas':media_horas,
    'grafico_hora' : grafico_hora,
    'grafico_semana': grafico_semana,
    'grafico_hora_url': grafico_hora_url,
    'grafico_semana_url': grafico_semana_url,
    'dias_ordenados': DIAS_ORDENADOS,

    }

    

    return render(request, 'relatorios/dashboard.html', context)





