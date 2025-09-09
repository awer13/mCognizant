# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from .forms import TeacherSignupForm, StudentSignupForm

def signup(request):
    """
    Единая страница регистрации.
    GET: ?role=teacher|student (по умолчанию student)
    POST: hidden/select name="role" из формы.
    """
    if request.method == "POST":
        role = request.POST.get("role", "STUDENT").upper()
        FormClass = TeacherSignupForm if role == "TEACHER" else StudentSignupForm
        form = FormClass(request.POST)
        if form.is_valid():
            user = form.save(role=role)
            login(request, user)
            return redirect("/")
    else:
        role_q = (request.GET.get("role") or "student").lower()
        FormClass = TeacherSignupForm if role_q == "teacher" else StudentSignupForm
        form = FormClass()

    # тот же signup.html, он уже умеет показывать селектор роли
    return render(request, "accounts/signup.html", {"form": form})

# Оставшиеся отдельные маршруты можно сохранить, но они больше не нужны
def signup_teacher(request):
    if request.method == "POST":
        form = TeacherSignupForm(request.POST)
        if form.is_valid():
            user = form.save(role="TEACHER")
            login(request, user)
            return redirect("/")
    else:
        form = TeacherSignupForm()
    return render(request, "accounts/signup.html", {"form": form})

def signup_student(request):
    if request.method == "POST":
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            user = form.save(role="STUDENT")
            login(request, user)
            return redirect("/")
    else:
        form = StudentSignupForm()
    return render(request, "accounts/signup.html", {"form": form})

class SignInView(LoginView):
    template_name = "accounts/login.html"

class SignOutView(LogoutView):
    next_page = "/"
