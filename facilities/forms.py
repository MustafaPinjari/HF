from django import forms
from .models import Booking, Event

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['facility', 'start_time', 'end_time', 'purpose']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'date', 'sponsor', 'budget', 'expenses', 'sponsorship_amount', 
                 'utilization_details', 'expense_proof', 'image']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'utilization_details': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter utilization details (one per line)'}),
        }