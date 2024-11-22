from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login_view'),  # Página de login
    path('welcome/', views.welcome_view, name='welcome_view'),  # Página de boas-vindas
    # path('messelection/', self.admin_site.admin_view(self.gerar_relatorio), name='messelection')

]
