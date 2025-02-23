from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Course, Enrollment, Attendance

class BaseUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    department = forms.ChoiceField(choices=User.DEPARTMENT_CHOICES, required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password1', 'password2',
            'first_name', 'last_name', 'department'
        ]

class StudentRegistrationForm(BaseUserRegistrationForm):
    division = forms.ChoiceField(choices=User.DIVISION_CHOICES, required=True)
    class_year = forms.ChoiceField(choices=User.CLASS_YEAR_CHOICES, required=True)

    class Meta(BaseUserRegistrationForm.Meta):
        fields = BaseUserRegistrationForm.Meta.fields + ['division', 'class_year']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
        return user

class FacultyRegistrationForm(BaseUserRegistrationForm):
    class Meta(BaseUserRegistrationForm.Meta):
        fields = BaseUserRegistrationForm.Meta.fields

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'faculty'
        if commit:
            user.save()
        return user

class AdminRegistrationForm(BaseUserRegistrationForm):
    class Meta(BaseUserRegistrationForm.Meta):
        fields = BaseUserRegistrationForm.Meta.fields

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'admin'
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture']

class HealthRequestForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['health_requests']

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['leave_requests']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'credits', 'department', 'semester', 'description']

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['course', 'semester', 'year']

class GradeUpdateForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['grade']

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['is_present']

class BulkAttendanceForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    def __init__(self, *args, **kwargs):
        students = kwargs.pop('students', [])
        super().__init__(*args, **kwargs)
        
        for student in students:
            self.fields[f'student_{student.id}'] = forms.BooleanField(
                label=student.get_full_name(),
                required=False
            )