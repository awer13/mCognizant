# exams/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ВАЖНО: НЕ создаём здесь свой Group!
# Ссылаемся на реальную модель из приложения courses по строке 'courses.ClassGroup'.

class Test(models.Model):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    STATES = [(DRAFT, "Черновик"), (PUBLISHED, "Опубликован")]

    title = models.CharField(max_length=200, default="Без названия")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tests")
    group = models.ForeignKey("courses.ClassGroup", on_delete=models.CASCADE, related_name="tests")  # ← вот так
    num_questions = models.PositiveIntegerField(default=5)
    max_score = models.PositiveIntegerField(default=100)
    state = models.CharField(max_length=12, choices=STATES, default=DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def publish(self):
        self.state = self.PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=["state", "published_at"])

    def __str__(self): 
        return f"{self.title} ({self.get_state_display()})"



class TestQuestion(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    order = models.PositiveIntegerField()  # 1..N
    topic_id = models.CharField(max_length=64)  # например 'series_class_1'
    # фиксируем параметры генерации; на этом воспроизводим постановку для всех
    payload_json = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = [("test", "order")]
        ordering = ["order"]

    def __str__(self): return f"Q{self.order} [{self.topic_id}]"


class TestAttempt(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attempts")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    total_score = models.FloatField(default=0)
    total_percent = models.FloatField(default=0)
    variant_seed = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = [("test", "student", "started_at")]

    def __str__(self): return f"Attempt #{self.id} {self.student} on {self.test}"


class TestAnswer(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name="answers")
    question_order = models.PositiveIntegerField()
    subq_key = models.CharField(max_length=64)  # например 'a_n', 'S_n', 'conv', 'reason'
    value = models.TextField(blank=True, default="")
    is_correct = models.BooleanField(default=False)
    score_awarded = models.FloatField(default=0)
    max_score = models.FloatField(default=0)
    feedback = models.TextField(blank=True, default="")

    class Meta:
        unique_together = [("attempt", "question_order", "subq_key")]
        ordering = ["question_order", "subq_key"]
