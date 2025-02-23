from django import forms
from .models import Election, Nomination

class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = [
            'title',
            'description',
            'nomination_start_date',
            'nomination_end_date',
            'voting_start_date',
            'voting_end_date'
        ]
        widgets = {
            'nomination_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'nomination_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'voting_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'voting_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class NominationForm(forms.ModelForm):
    class Meta:
        model = Nomination
        fields = ['manifesto', 'experience', 'achievements', 'profile_picture']
        widgets = {
            'manifesto': forms.Textarea(attrs={'rows': 4}),
            'experience': forms.Textarea(attrs={'rows': 4}),
            'achievements': forms.Textarea(attrs={'rows': 4}),
        }

class NominationAdminForm(forms.ModelForm):
    class Meta:
        model = Nomination
        fields = ['status', 'admin_remarks']
        widgets = {
            'admin_remarks': forms.Textarea(attrs={'rows': 4}),
        }