# generator_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('generate-task/', views.GenerateTaskView.as_view(), name='generate-task'),
]