# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.apps import apps

class BaseSignupForm(forms.ModelForm):
    username = forms.CharField(label="Имя пользователя")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Повторите пароль")

    class Meta:
        model = User
        fields = ("username",)

    def clean_username(self):
        u = self.cleaned_data["username"]
        if User.objects.filter(username=u).exists():
            raise forms.ValidationError("Такой логин уже занят.")
        return u

    def clean(self):
        cd = super().clean()
        p1, p2 = cd.get("password1"), cd.get("password2")
        if p1 != p2:
            self.add_error("password2", "Пароли не совпадают.")
        # базовые требования к паролю
        v = p1 or ""
        errs = []
        if len(v) < 8: errs.append("Минимум 8 символов.")
        if not any(c.islower() for c in v): errs.append("Нужна строчная буква.")
        if not any(c.isupper() for c in v): errs.append("Нужна заглавная буква.")
        if not any(c.isdigit() for c in v): errs.append("Нужна цифра.")
        if not any(not ch.isalnum() for ch in v): errs.append("Нужен спецсимвол.")
        if errs:
            self.add_error("password1", " ".join(errs))
        return cd

    def save(self, role):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.save()
        up = user.userprofile
        up.role = role
        up.save()
        return user


class TeacherSignupForm(BaseSignupForm):
    pass


class StudentSignupForm(BaseSignupForm):
    group_key = forms.CharField(
        label="Группа (ID или код)", required=False,
        help_text="Можно оставить пустым и вступить позже."
    )
    _group_obj = None  # внутренняя переменная для кэша найденной группы

    def clean_group_key(self):
        key = (self.cleaned_data.get("group_key") or "").strip()
        if not key:
            return key
        ClassGroup = apps.get_model("courses", "ClassGroup")
        try:
            if key.isdigit():
                self._group_obj = ClassGroup.objects.get(id=int(key))
            else:
                self._group_obj = ClassGroup.objects.get(enroll_code__iexact=key)
        except ClassGroup.DoesNotExist:  # type: ignore
            raise forms.ValidationError("Группа не найдена. Проверьте ID или код.")
        return key

    def save(self, role):
        user = super().save(role)
        key = (self.cleaned_data.get("group_key") or "").strip()
        if role == "STUDENT" and key and self._group_obj is not None:
            GroupMembership = apps.get_model("courses", "GroupMembership")
            GroupMembership.objects.get_or_create(user=user, group=self._group_obj)
        return user
