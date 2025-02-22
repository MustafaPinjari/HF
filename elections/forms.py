from django import forms
from .models import Nomination, Election

class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['title', 'description', 'start_date', 'end_date', 'nomination_end_date', 'is_active']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'nomination_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class NominationForm(forms.ModelForm):
    class Meta:
        model = Nomination
        fields = ['manifesto', 'experience', 'profile_picture']
        widgets = {
            'manifesto': forms.Textarea(attrs={'rows': 4}),
            'experience': forms.Textarea(attrs={'rows': 3}),
        }

class NominationAdminForm(forms.ModelForm):
    class Meta:
        model = Nomination
        fields = ['status', 'admin_remarks']
        widgets = {
            'admin_remarks': forms.Textarea(attrs={'rows': 3}),
        }