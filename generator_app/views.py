# generator_app/views.py

import json
import traceback
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.html import escape

from generator_app.registry import controller
from .analyzer import TaskAnalyzer
from .html_renderer import HTMLRenderer

# Твои генераторы
from .generators.series_generator_1 import SeriesGeneratorClass1
from .generators.series_generator_2 import SeriesGeneratorClass2
from .generators.series_generator_3 import SeriesGeneratorClass3
from .generators.series_generator_4 import SeriesGeneratorClass4


# --- Инициализация ядра/анализатора/рендерера ---
analyzer = TaskAnalyzer()
renderer = HTMLRenderer()

# Регистрация генераторов (автоматически попадут в селект)
controller.register_generator("series_class_1", SeriesGeneratorClass1)
controller.register_generator("series_class_2", SeriesGeneratorClass2)
controller.register_generator("series_class_3", SeriesGeneratorClass3)
controller.register_generator("series_class_4", SeriesGeneratorClass4)


# ---------- API тем для селекта ----------
@require_GET
def topics_api(request):
    """
    Возвращает список тем из реестра генераторов.
    Ожидаемый формат:
    [{"id": "...", "label": "...", "subCount": <int>}, ...]
    """
    topics = []
    # Пытаемся использовать controller.topics(), если он есть
    if hasattr(controller, "topics"):
        try:
            topics = controller.topics() or []
        except Exception:
            topics = []

    # Фоллбек: хотя бы отдать id'шники из приватного словаря
    if not topics:
        try:
            for k in getattr(controller, "_generators", {}).keys():
                # label = человеко-читаемое имя; subCount — по умолчанию 1
                topics.append({"id": k, "label": k, "subCount": 1})
        except Exception:
            # Последний фоллбек — твои 4 темы
            topics = [
                {"id": "series_class_1", "label": "Необходимое условие (1)", "subCount": 1},
                {"id": "series_class_2", "label": "Необходимое условие (2)", "subCount": 1},
                {"id": "series_class_3", "label": "Необходимое условие (3)", "subCount": 1},
                {"id": "series_class_4", "label": "Необходимое условие (4)", "subCount": 1},
            ]

    return JsonResponse({"topics": topics})


# ---------- Главная страница ----------
@ensure_csrf_cookie
def index_view(request):
    """
    Рендерит главную HTML-страницу портала (там мы уже подключили красивый вид).
    """
    return render(request, "generator_app/index.html")


# ---------- Генерация задачи (только TEACHER) ----------
@method_decorator(login_required, name="dispatch")
class GenerateTaskView(View):
    """
    POST /generate-task/
    body: {"task_type": "...", "complexity": 10}

    Возвращает: {"html": "..."} — HTML задачи (MathJax прогружается на фронте).
    Доступ только для роли TEACHER.
    """

    def post(self, request, *args, **kwargs):
        # Проверка роли
        role = getattr(getattr(request.user, "userprofile", None), "role", None)
        if role != "TEACHER":
            return JsonResponse({"error": "Доступ только для преподавателя"}, status=403)

        # Чтение payload
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный JSON"}, status=400)

        task_type = data.get("task_type")
        complexity = data.get("complexity")

        if not task_type:
            return JsonResponse({"error": "Не передан 'task_type'"}, status=400)

        # Генерация задачи через ядро
        try:
            task = controller.create_task(task_type, complexity=complexity)
        except Exception:
            # Если генератор внутри упал — вернём стек для дебага (можно скрыть в проде)
            return JsonResponse(
                {"error": "Ошибка генерации", "traceback": traceback.format_exc()},
                status=500,
            )

        if task is None:
            return JsonResponse({"error": f"Генератор '{task_type}' не найден"}, status=404)

        # Рендерим HTML. Если у HTMLRenderer другой интерфейс — подстрахуемся.
        try:
            if hasattr(renderer, "render"):
                html = renderer.render(task)
            else:
                # Совсем уж простой фоллбек
                html = f"<div class='task-container'><pre>{escape(str(task))}</pre></div>"
        except Exception:
            html = f"<div class='task-container'><pre>{escape(str(task))}</pre></div>"

        return JsonResponse({"html": html})
