# accounts/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    class Roles(models.TextChoices):
        TEACHER = "TEACHER", "Преподаватель"
        STUDENT = "STUDENT", "Студент"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
    role = models.CharField(max_length=16, choices=Roles.choices, default=Roles.STUDENT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"
