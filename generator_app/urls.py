from django.urls import path
from .views import index_view, GenerateTaskView, topics_api

urlpatterns = [
    path("", index_view, name="index"),
    path("generate-task/", GenerateTaskView.as_view(), name="generate_task"),
    path("api/topics/", topics_api, name="topics_api"),
]
