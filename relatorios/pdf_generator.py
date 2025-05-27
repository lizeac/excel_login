
from home.models import LoginRecord
from datetime import datetime, date, time
import random




from reportlab.lib.pagesizes import A4
# from django_setup import *
from home.models import LoginRecord
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from django.http import FileResponse
import io
from datetime import datetime, date, time
from relatorios.filter_setup import DataExtractor
import random


# x = datetime.time()
months_name = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
               'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
data_month = datetime.now().strftime('%m')
data_month = int(data_month)
month_name = months_name[data_month-1]
alunos = {
    'Ana Beatriz Moreira': '21230001',
    'Bruno Carvalho Santos': '21230002',
    'Camila Oliveira Ramos': '21230003',
    'Daniela Ferreira Costa': '21230004',
    'Eduardo Almeida Rocha': '21230005',
    'Fernanda Souza Lima': '21230006',
    'Gabriel Martins Silva': '21230007',
    'Helena Castro Barreto': '21230008',
    'Igor Teixeira Luz': '21230009',
    'Joana Pires Andrade': '21230010',
    'Kaio Mendes Ribeiro': '21230011',
    'Larissa Gomes Duarte': '21230012',
    'Matheus Nogueira Pinto': '21230013',
    'Natália Barbosa Reis': '21230014',
    'Otávio Farias Cunha': '21230015',
    'Patrícia Dias Monteiro': '21230016',
    'Rafael Menezes Braga': '21230017',
    'Sabrina Cunha Lopes': '21230018',
    'Thiago Rocha Fernandes': '21230019',
    'Vitória Macedo Tavares': '21230020',
    'Yasmin Andrade Luz': '21230021',
    'Lucas Viana Correia': '21230022',
    'Júlia Costa Moura': '21230023',
    'Pedro Henrique Torres': '21230024',
    'Marina Freitas Lopes': '21230025',
    'Diego Cardoso Bastos': '21230026',
    'Carolina Ribeiro Soares': '21230027',
    'Renan Lima Marques': '21230028',
    'Luana Carvalho Diniz': '21230029',
    'Vinícius Figueiredo Sales': '21230030'
}




cursos = ['bi', 'eng producao', 'eng eletrica']
servicos = ['consulta', 'pesquisa', 'referencia', 'circulacao']
dia_semana = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']

for i in range(100):
    hora = random.randint(8, 18)
    minutos = random.randint(0, 59)
    mes = random.randint(2, 4) 
    dia = random.randint(1, 20)
    ano = 2024
    nome_completo, matricula = random.choice(list(alunos.items()))
    servico = random.choice(servicos)
    data_acesso = date(ano, mes, dia)
    hora_acesso = time(hora, minutos)
    dia_da_semana = random.choice(dia_semana)
    curso = random.choice(cursos)
    #    
    # 
    LoginRecord.objects.create(
        nome_completo = nome_completo,
        matricula = matricula,
        curso = curso,
        hora_acesso = hora_acesso,
        data_acesso = data_acesso,
        servico = servico,
        dia_da_semana = dia_da_semana,
    )















































def gerar_pdf_relatorio(relatorio_body, header_relatorio="Relatório", pic_cabecalho_path="\excel_login\staticfiles\brasao_icti.png"):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4


    if pic_cabecalho_path:
        
        p.drawImage(pic_cabecalho_path, x=2*cm, y=altura - 4*cm, width=4*cm, height=4*cm)


    #Título(Header) Centralizado
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(largura / 2, altura - 2*cm, "Universidade Federal da Bahia")
    p.setFont("Helvetica", 12)
    p.drawCentredString(largura / 2, altura - 2.8*cm, "Instituto de Ciência, Tecnologia e Inovação")
    p.setFont("Helvetica", 11)
    p.drawCentredString(largura / 2, altura - 3.5*cm, "Biblioteca Valterlinda Queiroz")

    # Título do Relatório 
    p.setFont("Helvetica-Bold", 13)
    p.drawCentredString(largura / 2, altura - 5*cm, header_relatorio)

    # Conteúdo do relatório 
    p.setFont("Helvetica", 10)
    y = altura - 6*cm
    for linha in relatorio_body.strip().splitlines():
        if y < 2.5*cm:
            p.showPage()
            y = altura - 2*cm
        p.drawString(2*cm, y, linha)
        y -= 0.5*cm

    # Rodapé com data
    p.setFont("Helvetica-Oblique", 9)
    data_geracao = datetime.now().strftime('%d/%m/%Y')
    data_day = datetime.now().strftime('%d')
    data_year = datetime.now().strftime('%y')
    p.drawCentredString(largura - 2*cm, 2*cm, f"Gerado em {data_day} de {data_month} de {data_year}")

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"{header_relatorio}{data_geracao}.pdf")
