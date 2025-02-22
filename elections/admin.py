from django.contrib import admin
from .models import Election, Nomination, Vote

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'nomination_end_date', 'is_active')
    list_filter = ('is_active', 'start_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_date'

@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    list_display = ('user', 'election', 'status', 'created_at')
    list_filter = ('status', 'election', 'created_at')
    search_fields = ('user__username', 'user__email', 'manifesto')
    raw_id_fields = ('user', 'election')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(election__department=request.user.department)
    
    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data:
            # Send notification to user about status change
            if obj.status == 'approved':
                # Implementation for sending approval notification
                pass
            elif obj.status == 'rejected':
                # Implementation for sending rejection notification
                pass
        super().save_model(request, obj, form, change)

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'election', 'candidate', 'created_at')
    list_filter = ('election', 'created_at')
    search_fields = ('user__username', 'candidate__user__username')
    raw_id_fields = ('user', 'election', 'candidate')
