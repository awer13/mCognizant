# courses/models.py
from django.db import models
from django.contrib.auth.models import User
import secrets, string

def _gen_code(n=6):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(n))

class ClassGroup(models.Model):
    name = models.CharField(max_length=120)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_groups")
    # новый код приглашения (уникальный, можно оставить пустым — сгенерируем при сохранении)
    enroll_code = models.CharField(max_length=12, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.enroll_code:
            # гарантируем уникальность
            code = _gen_code()
            while ClassGroup.objects.filter(enroll_code=code).exists():
                code = _gen_code()
            self.enroll_code = code
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.enroll_code or '—'})"


class GroupMembership(models.Model):
    group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_memberships")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("group", "user"),)

    def __str__(self):
        return f"{self.user} → {self.group}"
