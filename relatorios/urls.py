from django.urls import path
from home.models import LoginRecord
from . import views
from . import pdf_view

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard_view'),
    path('relatorio-pdf/', pdf_view.gerar_pdf, name='pdf_view'),  # nova rota
]
