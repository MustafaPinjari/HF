from django import forms
from .models import Complaint, ComplaintResponse

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'description', 'is_anonymous']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ResponseForm(forms.ModelForm):
    class Meta:
        model = ComplaintResponse
        fields = ['response']