from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, HealthRecord

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'department', 'phone', 'is_active')
    list_filter = ('role', 'department', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'student_id')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'email', 'phone',
                'date_of_birth', 'profile_picture', 'bio', 'address'
            )
        }),
        ('Academic info', {
            'fields': ('role', 'department', 'student_id')
        }),
        ('Social Media', {
            'fields': ('linkedin_profile', 'github_profile'),
            'classes': ('collapse',)
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact',),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'department'),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(role__in=['faculty-sports', 'faculty-lab', 'faculty-transport', 'faculty-hod', 'faculty-teaching'])

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'condition', 'reported_by', 'date_reported')
    list_filter = ('date_reported', 'student__department')
    search_fields = ('student__username', 'condition', 'reported_by__username')
    date_hierarchy = 'date_reported'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(student__department=request.user.department)
