# accounts/urls.py
from django.urls import path
from .views import signup, signup_teacher, signup_student, SignInView, SignOutView

urlpatterns = [
    path("signup/", signup, name="signup"),  # ← единая страница
    path("signup/teacher/", signup_teacher, name="signup_teacher"),  # опционально
    path("signup/student/", signup_student, name="signup_student"),  # опционально
    path("login/", SignInView.as_view(), name="login"),
    path("logout/", SignOutView.as_view(), name="logout"),
]
