# task_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('generator_app.urls')), # <-- This line connects to your app's URLs
]