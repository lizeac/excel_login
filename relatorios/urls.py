from django.urls import path
from home.models import LoginRecord
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard_view'),
]
