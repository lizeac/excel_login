from django.shortcuts import render, redirect
from django.http import HttpResponse
from openpyxl import Workbook, load_workbook
from datetime import datetime
import os
from validate_docbr import CPF
from home.cpf_validator import check_mat
# Definir o arquivo Excel que será manipulado
month_names = month_name = {
            '1': 'Janeiro',
            '2': 'Fevereiro',
            '3': 'Março',
            '4': 'Abril',
            '5': 'Maio',
            '6': 'Junho',
            '7': 'Julho',
            '8': 'Agosto',
            '9': 'Setembro',
            '10': 'Outubro',
            '11': 'Novembro',
            '12': 'Dezembro'        
        }


dates = datetime.now()
month = dates.strftime('%m')
year = dates.strftime('%Y')
user_access_date = dates.strftime('%d/%m/%Y')
user_access_hour = dates.strftime('%H:%M')
file_to_handle = f'{month_name[str(int(month))]}_{year}.xlsx'
cpf = CPF()
# Verifica se o arquivo Excel já existe, caso contrário cria um novo
if not os.path.exists(file_to_handle):
    wb = Workbook()
    ws = wb.active
    ws.append(['Matrícula', 'Nome Completo', 'Serviço', 'Data de Acesso', 'Hora de Acesso', 'Visitante'])  # Cabeçalhos
    wb.save(file_to_handle)

def login_view(request):
    if request.method == 'POST':
        # Coleta os dados do formulário
        matricula = request.POST.get('matricula')
        nome_completo = request.POST.get('nome_completo')
        servico = request.POST.get('servico')
        # if request.POST.get('visitante') == None:
            
        
        # Verifica se algum campo está vazio
        if not matricula or not nome_completo or not servico:
            return HttpResponse("Todos os campos são obrigatórios. Volte e preencha todos os campos.")
        
        # Verifica se marcou o checkbox e se o cpf é valido
        if not request.POST.get('visitante'):
            visitante = 'Usuário UFBA'
        else:
            if cpf.validate(matricula):
                visitante = 'Visitante'
            else:
                return HttpResponse("O CPF digitado é invalido. Retorne e corrija as informações digitadas.")

        # Verifica se a matriula é valida, caso não seja visitante
        if visitante == 'Usuário UFBA' and not check_mat(matricula):
            print(f'chequei a matricla {matricula}, e ela é {check_mat(matricula)}')
            return HttpResponse("A Matricula é invalida. Volte e digite um valor válido.")

        if cpf.validate(matricula) or check_mat(matricula):
            try:
                # Carrega ou cria a planilha Excel
                wb = load_workbook(file_to_handle)
                ws = wb.active

                # Verifica se o usuário já fez login hoje
                for row in ws.iter_rows(values_only=True):
                    if matricula == row[0] and user_access_date == row[3]:
                        return HttpResponse("Você já fez login hoje!")

                # Adiciona os dados à planilha
                ws.append([matricula, nome_completo, servico, user_access_date, user_access_hour, visitante])
                wb.save(file_to_handle)

                # Redireciona para a página de boas-vindas
                # Coloquei isso aqui de novo pq tava inserindo no arquivo se voltasse na pagina depois de logar msm com 
                # dados invalidos
                
                return redirect('welcome_view')

            except Exception as e:
                return HttpResponse(f"Erro ao salvar os dados: {str(e)}")

    return render(request, 'login.html')

def welcome_view(request):
    return render(request, 'welcome.html')

