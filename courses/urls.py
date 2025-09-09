# courses/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("join/", views.join_group, name="courses_join_group"),
    path("my/", views.my_groups_page, name="courses_my_groups"),
    path("api/my/", views.api_my_groups, name="courses_api_my_groups"),
    path("api/create/", views.api_create_group, name="courses_api_create_group"),
]
