from django.contrib import admin
from .models import CheatingCase, Sanction, Appeal

@admin.register(CheatingCase)
class CheatingCaseAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'violation_type', 'severity', 'status', 'date_reported')
    list_filter = ('status', 'violation_type', 'severity')
    search_fields = ('student__username', 'course', 'description')
    date_hierarchy = 'date_reported'

@admin.register(Sanction)
class SanctionAdmin(admin.ModelAdmin):
    list_display = ('case', 'sanction_type', 'start_date', 'end_date', 'issued_by')
    list_filter = ('sanction_type',)
    search_fields = ('case__student__username', 'description')

@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = ('case', 'submitted_by', 'status', 'submission_date')
    list_filter = ('status',)
    search_fields = ('case__student__username', 'grounds')
