from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("generator_app.urls")),   # главная — твой генератор
    path("accounts/", include("accounts.urls")),
    path("courses/", include("courses.urls")),
    path("tests/", include("exams.urls")),
]
