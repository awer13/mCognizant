# exams/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # HTML
    path("builder/", views.builder_page, name="tests_builder"),
    path("my/", views.my_tests_page, name="exams_my_tests"),
    path("teacher/", views.teacher_tests_page, name="exams_teacher_tests"),
    path("run/<int:attempt_id>/", views.run_attempt_page, name="exams_run_attempt"),
    path("review/<int:attempt_id>/", views.review_attempt_page, name="exams_review_attempt"),

    # API (teacher)
    path("api/tests/", views.api_create_test, name="api_create_test"),
    path("api/tests/<int:test_id>/questions/", views.api_set_questions, name="api_set_questions"),
    path("api/tests/<int:test_id>/publish/", views.api_publish_test, name="api_publish_test"),
    path("api/teacher/tests/", views.api_teacher_tests, name="exams_api_teacher_tests"),
    path("api/tests/<int:test_id>/attempts/", views.api_test_attempts, name="exams_api_test_attempts"),

    # API (student)
    path("api/my/", views.api_my_tests, name="exams_api_my_tests"),
    path("api/tests/<int:test_id>/start/", views.api_start_attempt, name="exams_api_start_attempt"),

    # API для плеера
    path("api/attempts/<int:attempt_id>/question/<int:order>/", views.api_get_question, name="exams_api_get_question"),
    path("api/attempts/<int:attempt_id>/answer/<int:order>/", views.api_post_answer, name="exams_api_post_answer"),
    path("api/attempts/<int:attempt_id>/finish/", views.api_finish_attempt, name="exams_api_finish_attempt"),
]
