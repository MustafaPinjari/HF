from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    department = forms.ChoiceField(choices=User.DEPARTMENTS)
    role = forms.ChoiceField(choices=User.ROLES)
    profile_picture = forms.ImageField(required=False)
    
    class Meta:
        model = User
        fields = [
            'username', 
            'email', 
            'first_name', 
            'last_name',
            'password1', 
            'password2',
            'department',
            'role',
            'phone',
            'profile_picture'
        ]

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'profile_picture',
            'bio',
            'department',
            'linkedin_profile',
            'github_profile'
        ]

class HealthRequestForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['health_requests']

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['leave_requests']