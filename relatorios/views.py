from django.shortcuts import render
from django.db.models.functions import ExtractYear
from django.contrib.auth.decorators import user_passes_test, login_required
from home.models import LoginRecord
from home.constants import MONTHS, DIAS_ORDENADOS
# importar o banco de dados do que os alunos forneceram
from home.models import LoginRecord
from datetime import datetime
from relatorios.filter_setup import DataExtractor, filtro_de_periodo, contar_ocorrencias
from django.conf import settings
import os

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

    

    if ano_selecionado or mes_selecionado:
        ano_selecionado = request.GET.get('ano')
        mes_selecionado = request.GET.get('mes')
        queryset = filtro_de_periodo(ano_selecionado, mes_selecionado)
        contador_ocorrencias = contar_ocorrencias(ano_selecionado, mes_selecionado)

        
        extrator = DataExtractor(queryset.get('queryset', []), 
                                queryset.get('ano'), queryset.get('mes'), 
                                output_dir=settings.GRAFICOS_ROOT)   
        dados_gerais= extrator.calcular_totais() # dict
        usuario_assiduo =extrator.aluno_mais_frequente() # list
        curso_frequente = extrator.curso_mais_assiduo() # dict
        servico_frequente = extrator.servico_mais_utilizado() # dict
        max_dia_semana = extrator.max_dia_semana() # 
        media_dia_semana = contador_ocorrencias.get('media', {}) # dict
        media_horas = extrator.calcular_media_por_hora() # dict
        grafico_hora = extrator.gerar_graficos_hora(media_horas) # img
        grafico_semana= extrator.gerar_grafico_semana(list(media_dia_semana.values())) # img
        grafico_hora_url = f"{settings.GRAFICOS_URL}{os.path.basename(grafico_hora)}"
        grafico_semana_url = f"{settings.GRAFICOS_URL}{os.path.basename(grafico_semana)}"



    else:
        queryset = {
            'queryset': [],
            'ano': None,
            'mes': None
        }
        dados_gerais = {}
        usuario_assiduo = []
        curso_frequente = {}
        servico_frequente = {}
        max_dia_semana = {}
        media_dia_semana = []
        media_horas = {}
        grafico_hora = None
        grafico_hora_url = None
        grafico_semana = None
        grafico_semana_url = None


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
    'media_dia_semana':media_dia_semana,
    'media_horas':media_horas,
    'grafico_hora' : grafico_hora,
    'grafico_semana': grafico_semana,
    'grafico_hora_url': grafico_hora_url,
    'grafico_semana_url': grafico_semana_url,
    'dias_ordenados': DIAS_ORDENADOS,

    }


    return render(request, 'relatorios/dashboard.html', context)

# execução da classe




