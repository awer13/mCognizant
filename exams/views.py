# exams/views.py
import json
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.utils import timezone
from django.db.models import Count

from .models import Test, TestQuestion, TestAttempt
from generator_app.registry import controller
from generator_app.html_renderer import HTMLRenderer
from generator_app.analyzer import TaskAnalyzer  # <— используем твой analyzer напрямую

renderer = HTMLRenderer()
analyzer = TaskAnalyzer()

ClassGroup = apps.get_model("courses", "ClassGroup")
GroupMembership = apps.get_model("courses", "GroupMembership")


def _is_student(u):
    try:
        return u.is_authenticated and u.userprofile.role == "STUDENT"
    except Exception:
        return False


def _is_teacher(u):
    try:
        return u.is_authenticated and u.userprofile.role == "TEACHER"
    except Exception:
        return False


# ---------- HTML: конструктор теста ----------
@login_required
@require_GET
def builder_page(request):
    if not _is_teacher(request.user):
        return HttpResponseForbidden("Только для преподавателей")
    try:
        topics = controller.topics()
    except Exception:
        topics = [
            {"id": "series_class_1", "label": "Геометрический ряд — тип 1"},
            {"id": "series_class_2", "label": "Геометрический ряд — тип 2"},
            {"id": "series_class_3", "label": "Общий член — тип 3"},
            {"id": "series_class_4", "label": "Общий член — тип 4"},
        ]
    return render(request, "exams/builder.html", {"topics": topics})


# ---------- API: TEACHER ----------
@login_required
@require_POST
def api_create_test(request):
    if not _is_teacher(request.user):
        return JsonResponse({"error": "forbidden"}, status=403)

    data = json.loads(request.body or "{}")
    title = data.get("title") or "Новый тест"
    group_key = str(data.get("group_id") or "").strip()  # ID или код
    num_questions = max(1, min(30, int(data.get("num_questions", 5))))
    max_score = int(data.get("max_score", 100))

    # Поиск группы по id или enroll_code
    try:
        if group_key.isdigit():
            group = ClassGroup.objects.get(id=int(group_key))
        else:
            group = ClassGroup.objects.get(enroll_code__iexact=group_key)
    except ClassGroup.DoesNotExist:
        return JsonResponse({"error": f"Группа '{group_key}' не найдена."}, status=404)

    test = Test.objects.create(
        title=title,
        author=request.user,
        group=group,
        num_questions=num_questions,
        max_score=max_score,
    )
    return JsonResponse({"id": test.id, "state": test.state})


@login_required
@require_http_methods(["PUT"])
def api_set_questions(request, test_id: int):
    if not _is_teacher(request.user):
        return JsonResponse({"error": "forbidden"}, status=403)
    test = get_object_or_404(Test, id=test_id, author=request.user)
    data = json.loads(request.body or "{}")
    items = data.get("questions", [])  # [{order, topic_id}]
    if not items:
        return JsonResponse({"error": "empty"}, status=400)

    TestQuestion.objects.filter(test=test).delete()
    bulk = []
    for it in items:
        order = int(it.get("order"))
        topic = str(it.get("topic_id"))
        bulk.append(TestQuestion(test=test, order=order, topic_id=topic, payload_json={}))
    TestQuestion.objects.bulk_create(bulk)
    return JsonResponse({"ok": True, "count": len(bulk)})


@login_required
@require_POST
def api_publish_test(request, test_id: int):
    if not _is_teacher(request.user):
        return JsonResponse({"error": "forbidden"}, status=403)
    test = get_object_or_404(Test, id=test_id, author=request.user)

    # На публикации можно ничего не «компилировать», мы это сделаем на старте попытки.
    test.publish()
    return JsonResponse({"ok": True, "state": test.state})


# ---------- API: STUDENT ----------
@login_required
@require_POST
def api_start_attempt(request, test_id: int):
    # только студент
    try:
        if not _role_required(request.user, "STUDENT"):
            return JsonResponse({"error": "Только для студентов."}, status=403)

        # тест должен быть опубликован
        test = Test.objects.select_related("group").get(id=test_id, state=Test.PUBLISHED)
    except Test.DoesNotExist:
        return JsonResponse({"error": "Тест не найден или не опубликован."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Не удалось открыть тест: {e}"}, status=400)

    # проверка членства студента в группе теста
    GroupMembership = apps.get_model("courses", "GroupMembership")
    if GroupMembership is None:
        return JsonResponse({"error": "Не найдена модель членства в группе."}, status=500)

    if not GroupMembership.objects.filter(group=test.group, user=request.user).exists():
        return JsonResponse({"error": "Вы не состоите в этой группе."}, status=403)

    # одна попытка на тест (если нужна многократность — поменяй на create)
    attempt, _created = TestAttempt.objects.get_or_create(test=test, student=request.user)

    return JsonResponse({"attempt_id": attempt.id, "num_questions": test.num_questions})


@login_required
@require_GET
def api_get_question(request, attempt_id: int, order: int):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, student=request.user)
    q = get_object_or_404(TestQuestion, test=attempt.test, order=order)

    payload = (q.payload_json or {})
    steps = payload.get("steps", [])
    q_state = (attempt.answers_json or {}).get("questions", {}).get(str(order))
    if not q_state:
        return JsonResponse({"error": "bad_state"}, status=400)

    idx = int(q_state.get("current_step", 0))
    if idx >= len(steps):
        idx = max(0, len(steps) - 1)

    step = steps[idx] if steps else {}
    total_q = attempt.test.num_questions

    data = {
        "order": q.order,
        "total_questions": total_q,
        "statement_html": payload.get("statement_html") or "<p>Постановка появится позже.</p>",
        "step_index": idx,
        "total_steps": len(steps),
        "step": {
            "key": step.get("key", f"step{idx+1}"),
            "type": step.get("type", "input"),
            "label": step.get("label", f"Вопрос {idx+1}"),
            "hint": step.get("hint"),
            "options": step.get("options") if step.get("type") == "select" else None
        },
        "question_done": bool(q_state.get("done")),
        "nav": {
            "prev_allowed": idx > 0,
            "next_allowed": bool(q_state["steps"][idx]["ok"]) if steps else False
        }
    }
    return JsonResponse(data)


@login_required
@require_POST
def api_post_answer(request, attempt_id: int, order: int):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, student=request.user)
    q = get_object_or_404(TestQuestion, test=attempt.test, order=order)

    body = json.loads(request.body or "{}")
    value = body.get("value")
    step_key = body.get("key")  # получаем ключ шага из фронта

    payload = (q.payload_json or {})
    steps = payload.get("steps", [])

    state = attempt.answers_json or {}
    q_state = state.get("questions", {}).get(str(order))
    if not q_state:
        return JsonResponse({"error": "bad_state"}, status=400)

    idx = int(q_state.get("current_step", 0))
    if idx >= len(steps):
        return JsonResponse({"error": "no_more_steps"}, status=400)

    # Проверяем, что фронт прислал тот шаг, который сейчас активен
    current_key = steps[idx].get("key")
    if step_key and step_key != current_key:
        return JsonResponse({"error": "wrong_step"}, status=400)

    # Проверка через analyzer.check_step
    res = analyzer.check_step(q.topic_id, current_key, value, {"steps": steps})

    # Обновляем состояние
    q_state["steps"][idx]["value"] = value
    q_state["steps"][idx]["ok"] = bool(res.get("ok"))
    q_state["steps"][idx]["score"] = float(res.get("score", 0.0))

    if q_state["steps"][idx]["ok"]:
        q_state["current_step"] = idx + 1
        if q_state["current_step"] >= len(steps):
            q_state["done"] = True

    attempt.answers_json = state
    attempt.save(update_fields=["answers_json"])

    return JsonResponse({
        "ok": q_state["steps"][idx]["ok"],
        "score": q_state["steps"][idx]["score"],
        "correct": res.get("correct"),
        "next_step": q_state["current_step"],
        "question_done": q_state["done"]
    })


@login_required
@require_POST
def api_finish_attempt(request, attempt_id: int):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, student=request.user)

    state = attempt.answers_json or {}
    total = 0.0
    max_total = 0.0
    per_question = []

    for q in attempt.test.questions.order_by("order"):
        payload = q.payload_json or {}
        q_state = (state.get("questions") or {}).get(str(q.order), {})
        steps_state = q_state.get("steps", [])
        score_q = sum(float(s.get("score", 0.0)) for s in steps_state)
        max_q = float(q_state.get("max_points", sum(float(s.get("points", 0)) for s in (payload.get("steps") or []))))
        total += score_q
        max_total += max_q
        per_question.append({
            "order": q.order,
            "score": score_q,
            "max": max_q,
            "steps": steps_state
        })

    attempt.finished_at = timezone.now()
    attempt.score = total
    attempt.save(update_fields=["finished_at", "score", "answers_json"])

    pct = 0 if max_total == 0 else round(100.0 * total / max_total, 2)
    return JsonResponse({
        "ok": True,
        "total_points": total,
        "max_points": max_total,
        "percent": pct,
        "report": per_question,
        "review_url": f"/tests/review/{attempt.id}/"
    })


# ---------- списки тестов/попыток ----------
@login_required
@require_GET
def my_tests_page(request):
    if not _is_student(request.user):
        return HttpResponseForbidden("Только для студентов.")
    return render(request, "exams/my_tests.html")


@login_required
@require_GET
def api_my_tests(request):
    if not _is_student(request.user):
        return JsonResponse({"error": "forbidden"}, status=403)

    tests_qs = (
        Test.objects
        .filter(group__memberships__user=request.user, state=Test.PUBLISHED)
        .select_related("group", "author")
        .order_by("-id")
        .distinct()
    )
    attempts = TestAttempt.objects.filter(test__in=tests_qs, student=request.user)
    attempt_by_test = {a.test_id: a.id for a in attempts}

    data = []
    for t in tests_qs:
        data.append({
            "id": t.id,
            "title": t.title,
            "group": {"id": t.group_id, "name": t.group.name},
            "author": t.author.username if t.author_id else None,
            "num_questions": t.num_questions,
            "attempt_id": attempt_by_test.get(t.id),
        })
    return JsonResponse({"tests": data})


@login_required
@require_GET
def teacher_tests_page(request):
    if not _is_teacher(request.user):
        return HttpResponseForbidden("Только для преподавателей.")
    return render(request, "exams/teacher_tests.html")


@login_required
@require_GET
def api_teacher_tests(request):
    if not _is_teacher(request.user):
        return JsonResponse({"error": "forbidden"}, status=403)

    qs = (Test.objects.filter(author=request.user)
          .select_related("group")
          .order_by("-id"))

    counts = dict(
        TestAttempt.objects.filter(test__in=qs)
        .values_list("test_id")
        .annotate(c=Count("id"))
        .values_list("test_id", "c")
    )

    data = []
    for t in qs:
        data.append({
            "id": t.id,
            "title": t.title,
            "state": t.state,
            "num_questions": t.num_questions,
            "group": {"id": t.group_id, "name": t.group.name if t.group_id else None},
            "attempts_count": counts.get(t.id, 0),
        })
    return JsonResponse({"tests": data})


@login_required
@require_GET
def api_test_attempts(request, test_id: int):
    if not _is_teacher(request.user):
        return JsonResponse({"error": "forbidden"}, status=403)

    test = get_object_or_404(Test, id=test_id, author=request.user)
    atts = (TestAttempt.objects
            .filter(test=test)
            .select_related("student")
            .order_by("-id"))

    items = []
    for a in atts:
        items.append({
            "id": a.id,
            "student": a.student.username if a.student_id else None,
            "started_at": getattr(a, "created_at", None) or getattr(a, "started_at", None),
            "finished_at": getattr(a, "finished_at", None),
            "score": getattr(a, "score", None),
        })
    return JsonResponse({
        "test": {"id": test.id, "title": test.title},
        "attempts": items
    })


# ---------- страницы попытки/отчёта ----------
@login_required
@require_GET
def review_attempt_page(request, attempt_id: int):
    att = get_object_or_404(TestAttempt, id=attempt_id)
    if _is_teacher(request.user):
        if att.test.author_id != request.user.id:
            return HttpResponseForbidden("Нет доступа к этой попытке.")
    elif att.student_id != request.user.id:
        return HttpResponseForbidden("Нет доступа к этой попытке.")

    answers = getattr(att, "answers_json", None)
    ctx = {
        "attempt": att,
        "answers": answers,
        "score": getattr(att, "score", None),
        "started_at": getattr(att, "created_at", None) or getattr(att, "started_at", None),
        "finished_at": getattr(att, "finished_at", None),
    }
    return render(request, "exams/attempt_review.html", ctx)


@login_required
@require_GET
def run_attempt_page(request, attempt_id: int):
    """Экран прохождения попытки студентом."""
    attempt = get_object_or_404(TestAttempt, id=attempt_id, student=request.user)
    test = attempt.test
    num = getattr(test, "num_questions", 1) or 1
    q_range = list(range(1, num + 1))  # ← передаём в шаблон готовый range

    ctx = {
        "attempt": attempt,
        "num_questions": num,
        "q_range": q_range,           # ← новое поле
    }
    return render(request, "exams/run_attempt.html", ctx)
