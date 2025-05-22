from django.shortcuts import render
from django.db.models.functions import ExtractYear
from django.contrib.auth.decorators import user_passes_test, login_required
from home.models import LoginRecord
# importar o banco de dados do que os alunos forneceram
from home.models import LoginRecord
from datetime import datetime

MESES = [
    ("01", "Janeiro"),
    ("02", "Fevereiro"),
    ("03", "Março"),
    ("04", "Abril"),
    ("05", "Maio"),
    ("06", "Junho"),
    ("07", "Julho"),
    ("08", "Agosto"),
    ("09", "Setembro"),
    ("10", "Outubro"),
    ("11", "Novembro"),
    ("12", "Dezembro"),
]


# só permitir superusers
def superuser_required(user):
    return user.is_superuser

# # Create your views here.
@login_required(login_url='/admin/login/')
@user_passes_test(superuser_required)
def dashboard_view(request):
    # salvar os dados do que o usuario da dashboard selecionou
    ano_selecionado = request.GET.get('ano')
    mes_selecionado = request.GET.get('mes')

    # pegar os anos do banco de dados:
    anos_disponiveis = LoginRecord.objects.annotate(ano=ExtractYear('data_acesso')).values_list('ano', flat=True).distinct()
    # registros do banco de dados 
    registros = LoginRecord.objects.all()

    if ano_selecionado:
        registros = registros.filter(data_acesso__year=ano_selecionado)

    if mes_selecionado and mes_selecionado != "todos":
        registros = registros.filter(data_acesso__month=mes_selecionado)

    context = {
    'registros': registros,
    'ano_selecionado': ano_selecionado,
    'mes_selecionado': mes_selecionado,
    'anos_disponiveis': anos_disponiveis,
    'meses_disponiveis': MESES,
    }

    return render(request, 'relatorios/dashboard.html', context)


