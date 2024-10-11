from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login_view'),  # Página de login
    path('welcome/', views.welcome_view, name='welcome_view'),  # Página de boas-vindas
#    path('report/', generate_report, name='generate_report'), #Página de visualização dos relatórios mensais.

]
