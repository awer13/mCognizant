# courses/admin.py
from django.contrib import admin
from .models import ClassGroup, GroupMembership

class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0
    autocomplete_fields = ("user",)

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "teacher", "enroll_code")
    list_filter = ("teacher",)
    search_fields = ("name", "enroll_code", "teacher__username")
    inlines = [GroupMembershipInline]

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "user", "joined_at")
    list_filter = ("group",)
    search_fields = ("group__name", "group__enroll_code", "user__username")
