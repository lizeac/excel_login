from django.contrib import admin
from django.http import HttpResponse
from django.db.models import Count
from datetime import datetime
from .models import LoginRecord
from relatorios.pdf_generator import gerar_pdf_relatorio
from relatorios.extractor_data import DataExtractor


# criação das ações
@admin.action(description='Gerar Relatório do Mês Atual')
def gerar_relatorio_mes_atual(modeladmin, request, queryset):
    mes_atual = datetime.now().month
    return modeladmin.gerar_relatorio_mes_view(request, mes_atual)

@admin.action(description='Gerar Relatório do Ano Até Agora')
def gerar_relatorio_ano_atual(modeladmin, request, queryset):
    return modeladmin.gerar_relatorio_ano_view(request)

@admin.action(description='Mostrar Todos os Usuários do Ano')
def mostrar_todos_usuarios(modeladmin, request, queryset):
    ano_atual = datetime.now().year
    registros = LoginRecord.objects.filter(data_acesso__year=ano_atual)
    
    # HTML básico para listar os usuários, porque o render tava me dando trabalho
    html = """
    <html>
        <head><title>Usuários do Ano</title></head>
        <body>
            <h2>Lista de Todos os Usuários do Ano {}</h2>
            <table border="1" style="width:100%; border-collapse: collapse;">
                <tr>
                    <th>Matrícula</th>
                    <th>Nome Completo</th>
                    <th>Curso</th>
                    <th>Serviço</th>
                    <th>Data de Acesso</th>
                    <th>Hora de Acesso</th>
                    <th>Visitante</th>
                </tr>
    """.format(ano_atual)
    
    for registro in registros:
        html += """
            <tr>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
            </tr>
        """.format(
            registro.matricula,
            registro.nome_completo,
            registro.curso,
            registro.servico,
            registro.data_acesso.strftime('%d/%m/%Y'),
            registro.hora_acesso.strftime('%H:%M:%S'),
            registro.visitante
        )

    html += """
            </table>
        </body>
    </html>
    """
    
    return HttpResponse(html, content_type="text/html; charset=utf-8")

@admin.register(LoginRecord)
class LoginRecordAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'nome_completo', 'curso', 'servico', 'data_acesso', 'hora_acesso', 'visitante')
    search_fields = ('matricula', 'nome_completo', 'servico', 'visitante')
    list_filter = ('visitante', 'servico', 'data_acesso')
    actions = [gerar_relatorio_mes_atual, gerar_relatorio_ano_atual, mostrar_todos_usuarios]

    def gerar_relatorio_mes_view(self, request, mes):
        registros = LoginRecord.objects.filter(data_acesso__month=mes)

        # Total de visitantes do mês atual 
        total_visitantes_mes = registros.filter(visitante='Visitante').count() + \
                               registros.filter(visitante='Usuário UFBA').count()

        return self._gerar_relatorio_contexto(request, registros, mes=mes, total_visitantes=total_visitantes_mes)

    def gerar_relatorio_ano_view(self, request):
        ano_atual = datetime.now().year
        registros = LoginRecord.objects.filter(data_acesso__year=ano_atual)

        # Total de visitantes do ano atual
        total_visitantes_ano = registros.filter(visitante='Visitante').count() + \
                               registros.filter(visitante='Usuário UFBA').count()

        return self._gerar_relatorio_contexto(request, registros, ano=ano_atual, total_visitantes=total_visitantes_ano)
    


    #####################################################################################################################
    # gerar relatorios 
    def _gerar_relatorio_contexto(self, request, registros, mes=None, ano=None, total_visitantes=0):
        
        if mes:
            relatorio = DataExtractor(mes)
            header = f"Relatório do mês {mes}"
        else:
            relatorio = "Relatório anual ainda não implementado."
            header = "Relatório Anual"

        return gerar_pdf_relatorio(relatorio, header_relatorio=header)