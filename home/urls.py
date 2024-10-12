from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login_view'),  # Página de login
    path('welcome/', views.welcome_view, name='welcome_view'),  # Página de boas-vindas
    # path('relatorio/', views.relatorio_acessos, name='relatorio_acessos'), #Página de visualização dos relatórios mensais.

]
