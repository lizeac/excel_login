from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import LoginRecord  # Importar o modelo  que criei
from validate_docbr import CPF
from datetime import datetime
from openpyxl import Workbook, load_workbook

arquivo = 'matricula_alunos.xlsx'

wb = load_workbook(arquivo)
ws = wb['Alunos']


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
            today = datetime.now().date()
            if LoginRecord.objects.filter(matricula=matricula, data_acesso=today).exists():
                return HttpResponse("Você já fez login hoje!")

            # Armazena os dados no banco de dados
            LoginRecord.objects.create(
                matricula=matricula,
                nome_completo=nome_completo,
                servico=servico,
                data_acesso=today,
                hora_acesso=datetime.now().time(),
                visitante=visitante
            )

            return redirect('welcome_view')

    return render(request, 'login.html')

def welcome_view(request):
    return render(request, 'welcome.html')