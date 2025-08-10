# generator_app/urls.py
from django.urls import path
from . import views

from .views import GenerateTestView


urlpatterns = [
    path('', views.index_view, name='index'),
    path('generate-task/', views.GenerateTaskView.as_view(), name='generate-task'),
    path('test-generator/', views.test_generator_view, name='test-generator'),
    path('generate-test/', GenerateTestView.as_view(), name='generate-test'),
]