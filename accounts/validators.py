# accounts/validators.py
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class ComplexityValidator:
    """
    Требования:
      - хотя бы 1 строчная буква
      - хотя бы 1 заглавная буква
      - хотя бы 1 цифра
      - хотя бы 1 спецсимвол
    (длина >= 8 уже проверяет MinimumLengthValidator в settings.py)
    """
    def validate(self, password, user=None):
        if not re.search(r"[a-z]", password):
            raise ValidationError(_("Пароль должен содержать хотя бы одну строчную букву."))
        if not re.search(r"[A-Z]", password):
            raise ValidationError(_("Пароль должен содержать хотя бы одну заглавную букву."))
        if not re.search(r"\d", password):
            raise ValidationError(_("Пароль должен содержать хотя бы одну цифру."))
        if not re.search(r"[^\w\s]", password):
            raise ValidationError(_("Пароль должен содержать хотя бы один спецсимвол."))

    def get_help_text(self):
        return _("Минимум 8 символов, со строчной и заглавной буквой, цифрой и спецсимволом.")
