from django.contrib import admin
from django.http import HttpResponse
from django.db.models import Count
from datetime import datetime
from .models import LoginRecord

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
    
    # HTML básico para listar os usuários
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

    def _gerar_relatorio_contexto(self, request, registros, mes=None, ano=None, total_visitantes=0):
        visitante_mais_frequente = registros.values('matricula', 'nome_completo').annotate(
            total_acessos=Count('id')
        ).order_by('-total_acessos').first()

        data_com_mais_logins = registros.values('data_acesso').annotate(
            total_logins=Count('id')
        ).order_by('-total_logins').first()

        servico_mais_utilizado = registros.values('servico').annotate(
            total_utilizacoes=Count('id')
        ).order_by('-total_utilizacoes').first()

        curso_mais_frequente = registros.values('curso').annotate(
            total_logins=Count('id')
        ).order_by('-total_logins').first()

        am_visitas = registros.filter(hora_acesso__lt='12:00:00').count()
        pm_visitas = registros.filter(hora_acesso__gte='12:00:00').count()
        periodo_mais_frequente = 'Manhã' if am_visitas > pm_visitas else 'Tarde'

        total_usuarios_ufba = registros.filter(visitante='Usuário UFBA').count()
        total = total_visitantes  # Agora usando a variável passada
        percentual_visitantes = (total_visitantes / total) * 100 if total > 0 else 0
        percentual_ufba = (total_usuarios_ufba / total) * 100 if total > 0 else 0

        # Contagem de cada serviço
        contagem_servicos = registros.values('servico').annotate(total=Count('id')).order_by('-total')

        # Formatação dos serviços
        servicos_str = "\n".join([f"           - {servico['servico']}: {servico['total']} utilizações" for servico in contagem_servicos])

        relatorio = f"""
        Relatório {'do Mês' if mes else 'do Ano'}
        {'Mês: ' + str(mes) if mes else 'Ano: ' + str(ano)}
        
        Total de Visitantes: {total_visitantes}  # Novo total de visitantes
        
        1. Visitante Mais Frequente:
        - Nome: {visitante_mais_frequente.get('nome_completo', 'N/A')}
        - Total de Acessos: {visitante_mais_frequente.get('total_acessos', 0)}
        
        2. Data com Mais Logins:
        - Data: {data_com_mais_logins.get('data_acesso', 'N/A')}
        - Total de Logins: {data_com_mais_logins.get('total_logins', 0)}
        
        3. Serviço Mais Utilizado:
        - Serviço: {servico_mais_utilizado.get('servico', 'N/A')}
        - Total de Utilizações: {servico_mais_utilizado.get('total_utilizacoes', 0)}

        4. Curso Mais Frequente:
        - Curso: {curso_mais_frequente.get('curso', 'N/A')}
        - Total de Logins: {curso_mais_frequente.get('total_logins', 0)}
        
        5. Período Mais Frequente:
        - Período: {periodo_mais_frequente}
        
        6. Percentual de Visitantes:
        - Visitantes: {percentual_visitantes:.2f}%
        - Usuários UFBA: {percentual_ufba:.2f}%
        
        7. Utilizações por Serviço:
        {servicos_str}
        """
        return HttpResponse(relatorio, content_type="text/plain; charset=utf-8")
