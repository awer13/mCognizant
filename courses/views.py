# courses/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.apps import apps
import json

def _is_student(user) -> bool:
    try:
        return user.is_authenticated and user.userprofile.role == "STUDENT"
    except Exception:
        return False

def _is_teacher(user) -> bool:
    try:
        return user.is_authenticated and user.userprofile.role == "TEACHER"
    except Exception:
        return False


# ---------- Вступление в группу (студент) ----------
@login_required
def join_group(request):
    """
    Страница для студента: вступить в группу по ID или коду приглашения.
    """
    if not _is_student(request.user):
        return HttpResponseForbidden("Доступно только студентам.")

    ClassGroup = apps.get_model("courses", "ClassGroup")
    GroupMembership = apps.get_model("courses", "GroupMembership")

    ctx = {
        "memberships": GroupMembership.objects.filter(user=request.user).select_related("group"),
        "ok": None,
        "error": None,
        "entered": "",
    }

    if request.method == "POST":
        key = (request.POST.get("group_key") or "").strip()
        ctx["entered"] = key
        if not key:
            ctx["error"] = "Введите ID или код группы."
        else:
            try:
                if key.isdigit():
                    group = ClassGroup.objects.get(id=int(key))
                else:
                    group = ClassGroup.objects.get(enroll_code__iexact=key)
            except ClassGroup.DoesNotExist:  # type: ignore
                ctx["error"] = "Группа не найдена. Проверьте ID/код."
            else:
                if GroupMembership.objects.filter(user=request.user, group=group).exists():
                    ctx["ok"] = f"Вы уже состоите в группе «{group.name}»."
                else:
                    GroupMembership.objects.create(user=request.user, group=group)
                    ctx["ok"] = f"Готово! Вы присоединились к группе «{group.name}»."
                    ctx["memberships"] = GroupMembership.objects.filter(user=request.user).select_related("group")

    return render(request, "courses/join_group.html", ctx)


# ---------- Мои группы (страница) ----------
@login_required
@require_GET
def my_groups_page(request):
    """
    Страница 'Мои группы':
    - для преподавателя: список его групп + код приглашения
    - для студента: список его членств
    """
    ClassGroup = apps.get_model("courses", "ClassGroup")
    GroupMembership = apps.get_model("courses", "GroupMembership")

    if _is_teacher(request.user):
        groups = ClassGroup.objects.filter(teacher=request.user).order_by("id")
        ctx = {"role": "TEACHER", "groups": groups}
    elif _is_student(request.user):
        memberships = GroupMembership.objects.filter(user=request.user).select_related("group").order_by("group__id")
        ctx = {"role": "STUDENT", "memberships": memberships}
    else:
        return HttpResponseForbidden("Доступно только авторизованным пользователям с ролью.")

    return render(request, "courses/my_groups.html", ctx)


# ---------- API: получить мои группы JSON ----------
@login_required
@require_GET
def api_my_groups(request):
    ClassGroup = apps.get_model("courses", "ClassGroup")
    GroupMembership = apps.get_model("courses", "GroupMembership")

    if _is_teacher(request.user):
        groups = list(
            ClassGroup.objects.filter(teacher=request.user)
            .order_by("id")
            .values("id", "name", "enroll_code")
        )
        return JsonResponse({"role": "TEACHER", "groups": groups})

    if _is_student(request.user):
        ms = (
            GroupMembership.objects.filter(user=request.user)
            .select_related("group")
            .order_by("group__id")
        )
        groups = [{"id": m.group.id, "name": m.group.name, "enroll_code": m.group.enroll_code} for m in ms]
        return JsonResponse({"role": "STUDENT", "groups": groups})

    return JsonResponse({"error": "forbidden"}, status=403)


# ---------- API: создать группу (только преподаватель) ----------
@login_required
@require_POST
def api_create_group(request):
    if not _is_teacher(request.user):
        return JsonResponse({"error": "forbidden"}, status=403)

    ClassGroup = apps.get_model("courses", "ClassGroup")

    try:
        data = json.loads(request.body or "{}")
    except Exception:
        data = {}

    name = (data.get("name") or "").strip()
    if not name:
        return JsonResponse({"error": "Укажите название группы."}, status=400)

    g = ClassGroup.objects.create(name=name, teacher=request.user)  # enroll_code сгенерится в save()
    return JsonResponse({"id": g.id, "name": g.name, "enroll_code": g.enroll_code})
