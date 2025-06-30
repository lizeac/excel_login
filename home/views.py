from django.shortcuts import render, redirect
from django.http import HttpResponse
from home.models import LoginRecord  # Importar o modelo  que criei
from validate_docbr import CPF
from datetime import datetime
from openpyxl import load_workbook
from django.db.models import Count
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from home.constants import MATRICULA_STUDENTS

dates = datetime.now().date()
# month = dates.strftime('%m')
# year = dates.strftime('%Y')
# user_access_date = dates.strftime('%d/%m/%Y')
user_access_hour = datetime.now().time()

#Arquivo onde checo se a matricula dos alunos é valida
arquivo = MATRICULA_STUDENTS


wb = load_workbook(arquivo)
ws = wb['Alunos']

# colocando coisas no excel
c = []
for r in ws:
    for w in r:
        c.append(w.value)


def check_mat(n_matricula):
    is_valid = False
    for item in c:
        if n_matricula in item:
            is_valid = True
            print('Encontrou a matricula')
            return is_valid
    return is_valid


cpf = CPF()

def login_view(request):
    if request.method == 'POST':
        matricula = request.POST.get('matricula')
        nome_completo = request.POST.get('nome_completo')
        servico = request.POST.get('servico')
        curso = request.POST.get('curso')

        if not matricula or not nome_completo or not servico:
            return HttpResponse("Todos os campos são obrigatórios. Volte e preencha todos os campos.")
        
        if not request.POST.get('visitante'):
            visitante = 'Usuário UFBA'
        else:
            if cpf.validate(matricula):
                visitante = 'Visitante'
            else:
                return HttpResponse("O CPF digitado é inválido. Retorne e corrija as informações digitadas.")

        if visitante == 'Usuário UFBA' and not check_mat(matricula):
            return HttpResponse("A matrícula é inválida. Volte e digite um valor válido.")

        if cpf.validate(matricula) or check_mat(matricula):
            # Verifica se o usuário já fez login hoje

            if LoginRecord.objects.filter(matricula=matricula, data_acesso=dates).exists():
                return HttpResponse("Você já fez login hoje!")

            # Armazena os dados no banco de dados
            LoginRecord.objects.create(
                matricula=matricula,
                nome_completo=nome_completo,
                servico=servico,
                data_acesso=dates,
                hora_acesso=user_access_hour,
                visitante=visitante,
                curso = curso,
                )
            return redirect('welcome_view')

    return render(request, 'home/login.html')



def welcome_view(request):
    return render(request, 'home/welcome.html')


