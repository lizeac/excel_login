from django.contrib import admin

# Register your models here.
from .models import LoginRecord

class LoginRecordAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'nome_completo', 'servico', 'data_acesso', 'hora_acesso', 'visitante')
    search_fields = ('matricula', 'nome_completo')

admin.site.register(LoginRecord, LoginRecordAdmin)