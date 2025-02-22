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
        fields = ['title', 'date', 'sponsor', 'budget', 'expenses', 'sponsorship_amount', 'utilization_details', 'expense_proof']