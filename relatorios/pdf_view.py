from django.http import FileResponse, HttpResponseBadRequest, Http404
from django.conf import settings
from home.constants import MONTHS, DIAS_ORDENADOS
from relatorios.filter_setup import DataExtractor, contar_ocorrencias, filtro_de_periodo
from datetime import datetime
import os
from io import BytesIO
from django.shortcuts import render
from home.models import LoginRecord
from home.constants import MONTHS, DIAS_ORDENADOS
# importar o banco de dados do que os alunos forneceram
from home.models import LoginRecord
from relatorios.filter_setup import DataExtractor, contar_ocorrencias, filtro_de_periodo
from django.conf import settings
import os
from django.http import FileResponse


from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def gerar_pdf(request):
    ano_selecionado = request.GET.get('ano')
    mes_selecionado = request.GET.get('mes')

    if not ano_selecionado or ano_selecionado.strip().lower() == 'none':
        ano_nome = 'todos'
    
    else:
        ano_nome = ano_selecionado.strip()

    if not mes_selecionado or mes_selecionado.strip().lower() == 'none':
        mes_nome = 'todos'
    else:
        mes_nome = mes_selecionado.strip()
        
    
    if ano_selecionado is None or mes_selecionado is None:
        return HttpResponseBadRequest("Parâmetros obrigatórios: ano e mês.")
    contador_ocorrencias = contar_ocorrencias(ano_selecionado, mes_selecionado)
    print(f'\033[94m----- Retornando dados referentes a mês: {mes_selecionado} e ano: {ano_selecionado} -----\033[0m')

    mes_extenso = next((nome for numero, nome in MONTHS if str(numero) == str(mes_selecionado)), f"Mês {mes_nome}")

    path_hora = os.path.join(settings.GRAFICOS_ROOT, f"grafico_media_hora_{mes_nome}_{ano_nome}.png")
    path_dia = os.path.join(settings.GRAFICOS_ROOT, f"grafico_media_dia_semana_{mes_nome}_{ano_nome}.png")

    if not os.path.exists(path_hora) or not os.path.exists(path_dia):
        raise Http404("Gráficos não encontrados. Acesse a dashboard primeiro.")

    queryset = filtro_de_periodo(ano_selecionado, mes_selecionado)
    registros = queryset.get('queryset', [])
    extrator = DataExtractor(registros, ano_selecionado, mes_selecionado, output_dir=settings.GRAFICOS_ROOT)


    dados_gerais = extrator.calcular_totais()
    usuario_assiduo = extrator.aluno_mais_frequente()
    curso_frequente = extrator.curso_mais_assiduo()
    servico_frequente = extrator.servico_mais_utilizado()
    max_dia_semana = extrator.max_dia_semana()
    valores_dia_semana_dict = contador_ocorrencias
    print(f'\033[94m-----   {valores_dia_semana_dict}  -----   \033[0m')
    
    valores_dia_semana = [valores_dia_semana_dict.get(dia, 0) for dia in DIAS_ORDENADOS]

    print()
    print(f'\033[94m----- depois de ordenar  {valores_dia_semana}  -----   \033[0m')
    media_horas = extrator.calcular_media_por_hora()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_bold = styles['Heading4']
    style_title = ParagraphStyle('TitleCenter', parent=styles['Title'], alignment=1)
    elements = []

    # Cabeçalho
    brasao_path = 'relatorios/static/brasao_icti.png'
    if os.path.exists(brasao_path):
        elements.append(Image(brasao_path, width=3*cm, height=3*cm))
        elements.append(Spacer(1, 0.3*cm))

    elements.append(Paragraph("UNIVERSIDADE FEDERAL DA BAHIA", style_bold))
    elements.append(Paragraph("INSTITUTO DE CIÊNCIA, TECNOLOGIA E INFORMAÇÃO", style_bold))
    elements.append(Paragraph("BIBLIOTECA VALTERLINDA QUEIROZ", style_bold))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"Relatório do Ano: {ano_nome.capitalize()} — Mês: {mes_extenso.capitalize()}", style_title))
    elements.append(Spacer(1, 1*cm))

    # Dados gerais
    elements.append(Paragraph("<b>📊 Dados Gerais</b>", style_bold))
    elements.append(Paragraph(f"Total de acessos: {dados_gerais.get('total_acessos', 0)}", style_normal))
    elements.append(Paragraph(f"Total de Visitantes: {dados_gerais.get('total_visitantes', 0)}", style_normal))
    elements.append(Paragraph(f"Total de Usuários da UFBA: {dados_gerais.get('total_usuario_ufba', 0)}", style_normal))
    elements.append(Spacer(1, 0.5*cm))

    # Usuários mais assíduos
    elements.append(Paragraph("<b>👥 Usuários mais assíduos:</b>", style_bold))
    for usuario in usuario_assiduo:
        elements.append(Paragraph(f"Nome: {usuario.get('nome_completo', 'desconhecido')}", style_normal))
        elements.append(Paragraph(f"Matrícula: {usuario.get('matricula', 'desconhecida')}", style_normal))
        elements.append(Paragraph(f"Curso: {usuario.get('curso', 'desconhecido')}", style_normal))
        elements.append(Paragraph(f"Total de Acessos: {usuario.get('total', 0)}", style_normal))
        elements.append(Spacer(1, 0.2*cm))
    elements.append(Spacer(1, 0.4*cm))

    # Curso + Serviço + Dia com maior fluxo
    elements.append(Paragraph(f"<b>🎓 Curso com mais acessos:</b> {curso_frequente.get('curso', 'desconhecido')} — Total: {curso_frequente.get('total', 0)}", style_normal))
    elements.append(Paragraph(f"<b>🛠️ Serviço mais utilizado:</b> {servico_frequente.get('servico', 'desconhecido')} — Total: {servico_frequente.get('total', 0)}", style_normal))
    elements.append(Paragraph(f"<b>📅 Dia da semana com mais acessos:</b> {max_dia_semana.get('dia_da_semana', 'desconhecido')} — Total: {max_dia_semana.get('total', 0)}", style_normal))
    elements.append(Spacer(1, 0.5*cm))

    # Tabela: média por dia da semana
    data_semana = [["Dia", "Total de acessos"]]
    for dia, valor in zip(DIAS_ORDENADOS, valores_dia_semana):
        data_semana.append([dia, str(valor)])
    tabela_semana = Table(data_semana, hAlign='LEFT')
    tabela_semana.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ]))
    elements.append(Paragraph("<b>📈 Total de acessos por dia da semana:</b>", style_bold))
    elements.append(tabela_semana)
    elements.append(Spacer(1, 0.5*cm))

    # Tabela: média por hora
    data_hora = [["Hora", "Média de acessos"]]
    for hora, media in media_horas.items():
        data_hora.append([f"{hora}:00", f"{media:.4f}"])
    tabela_hora = Table(data_hora, hAlign='LEFT')
    tabela_hora.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ]))
    elements.append(Paragraph("<b>🕗 Média de acessos por hora:</b>", style_bold))
    elements.append(tabela_hora)
    elements.append(Spacer(1, 1*cm))


    # Página de gráficos
    elements.append(PageBreak())
    elements.append(Paragraph("<b>📊 Gráfico — Média de acessos por hora</b>", style_bold))
    elements.append(Image(path_hora, width=16*cm, height=8*cm))
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph("<b>📈 Gráfico — Média de acessos por dia da semana</b>", style_bold))
    elements.append(Image(path_dia, width=16*cm, height=8*cm))

    # Rodapé com data
    data_atual = datetime.today().strftime("Camaçari, %d de %B de %Y.")
    elements.append(Paragraph(data_atual, style_normal))

    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, content_type='application/pdf')
