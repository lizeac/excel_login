
from django.contrib import admin
from django.http import HttpResponse
from django.db.models import Count
from datetime import datetime
from .models import LoginRecord

@admin.action(description='Gerar Relatório')
def gerar_relatorio(modeladmin, request, queryset):
    # Visitante mais frequente do mês
    # mes_atual = datetime.now().month
    visitante_mais_frequente = LoginRecord.objects.filter(
        # data_acesso__month=mes_atual
    ).values('matricula', 'nome_completo').annotate(
        total_acessos=Count('id')
    ).order_by('-total_acessos').first()
    
    # Data com mais logins
    data_com_mais_logins = LoginRecord.objects.values('data_acesso').annotate(
        total_logins=Count('id')
    ).order_by('-total_logins').first()

    # Serviço mais utilizado
    servico_mais_utilizado = LoginRecord.objects.values('servico').annotate(
        total_utilizacoes=Count('id')
    ).order_by('-total_utilizacoes').first()

    # Curso mais frequente
    curso_mais_frequente = LoginRecord.objects.values('curso').annotate(
        total_logins=Count('id')
    ).order_by('-total_logins').first()

    # Pessoa mais frequente (matrícula)
    pessoa_mais_frequente = LoginRecord.objects.values('matricula', 'nome_completo').annotate(
        total_acessos=Count('id')
    ).order_by('-total_acessos').first()

    # Período do dia com mais visitas (AM/PM)
    am_visitas = LoginRecord.objects.filter(
        hora_acesso__lt='12:00:00'
    ).count()

    pm_visitas = LoginRecord.objects.filter(
        hora_acesso__gte='12:00:00'
    ).count()

    periodo_mais_frequente = 'AM' if am_visitas > pm_visitas else 'PM'

    # Proporção de visitantes versus usuários UFBA
    total_visitantes = LoginRecord.objects.filter(visitante='Visitante').count()
    total_usuarios_ufba = LoginRecord.objects.filter(visitante='Usuário UFBA').count()
    total = total_visitantes + total_usuarios_ufba
    percentual_visitantes = (total_visitantes / total) * 100 if total > 0 else 0
    percentual_ufba = (total_usuarios_ufba / total) * 100 if total > 0 else 0

    # Gerar HTML para exibir no Admin
    html = f"""
    <h2>Relatório de Acessos</h2>
    <p><strong>Visitante mais frequente do mês:</strong> {visitante_mais_frequente['nome_completo'] if visitante_mais_frequente else 'Nenhum'}</p>
    <p><strong>Data com mais logins:</strong> {data_com_mais_logins['data_acesso'] if data_com_mais_logins else 'Nenhum'}</p>
    <p><strong>Serviço mais utilizado:</strong> {servico_mais_utilizado['servico'] if servico_mais_utilizado else 'Nenhum'}</p>
    <p><strong>Curso mais frequente:</strong> {curso_mais_frequente['curso'] if curso_mais_frequente else 'Nenhum'}</p>
    <p><strong>Matrícula da pessoa mais frequente:</strong> {pessoa_mais_frequente['matricula'] if pessoa_mais_frequente else 'Nenhuma'}</p>
    <p><strong>Período do dia com mais visitas:</strong> {periodo_mais_frequente}</p>
    <p><strong>Proporção de visitantes:</strong> {percentual_visitantes:.2f}%</p>
    <p><strong>Proporção de usuários UFBA:</strong> {percentual_ufba:.2f}%</p>
    """

    return HttpResponse(html)

@admin.register(LoginRecord)
class LoginRecordAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'nome_completo', 'curso', 'servico', 'data_acesso', 'hora_acesso', 'visitante')
    search_fields = ('matricula', 'nome_completo', 'servico', 'visitante')
    list_filter = ('visitante', 'servico', 'data_acesso')
    actions = [gerar_relatorio]
