
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




from home.models import LoginRecord

LoginRecord.objects.filter(data_acesso__year=2024, data_acesso__month=4).count()









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
    data_month = datetime.now().strftime('%m')
    data_year = datetime.now().strftime('%y')
    p.drawCentredString(largura - 2*cm, 2*cm, f"Gerado em {data_day} de {data_month} de {data_year}")

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"{header_relatorio}{data_geracao}.pdf")
