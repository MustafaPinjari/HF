from django import forms
from .models import CheatingCase, Sanction, Appeal

class CheatingCaseForm(forms.ModelForm):
    class Meta:
        model = CheatingCase
        fields = [
            'student', 'course', 'exam_date', 'violation_type',
            'severity', 'description', 'evidence'
        ]
        widgets = {
            'exam_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class SanctionForm(forms.ModelForm):
    class Meta:
        model = Sanction
        fields = ['sanction_type', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class AppealForm(forms.ModelForm):
    class Meta:
        model = Appeal
        fields = ['grounds', 'supporting_evidence']
        widgets = {
            'grounds': forms.Textarea(attrs={'rows': 4}),
        }

class CaseUpdateForm(forms.ModelForm):
    class Meta:
        model = CheatingCase
        fields = ['status', 'resolution_notes']
        widgets = {
            'resolution_notes': forms.Textarea(attrs={'rows': 3}),
        }