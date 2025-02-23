from django.contrib import admin
from .models import Election, Nomination, Candidate, Vote
from django.utils import timezone

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'nomination_start_date',
        'nomination_end_date',
        'voting_start_date',
        'voting_end_date',
        'created_at'
    ]
    list_filter = [
        'nomination_start_date',
        'nomination_end_date',
        'voting_start_date',
        'voting_end_date'
    ]
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'

@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    list_display = ['user', 'election', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'election__title']
    raw_id_fields = ['user', 'election']
    
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

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['user', 'election', 'votes_count']
    list_filter = ['election']
    search_fields = ['user__username', 'election__title']
    raw_id_fields = ['user', 'election', 'nomination']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['voter', 'election', 'candidate', 'timestamp']
    list_filter = ['election', 'timestamp']
    search_fields = ['voter__username', 'candidate__user__username']
    raw_id_fields = ['voter', 'election', 'candidate']
