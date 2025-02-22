from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLES = (
        ('student', 'Student'),
        ('faculty-sports', 'Faculty - Sports'),
        ('faculty-lab', 'Faculty - Lab'),
        ('faculty-transport', 'Faculty - Transport'),
        ('faculty-hod', 'Faculty - HOD'),
        ('faculty-teaching', 'Faculty - Teaching Staff'),
        ('admin', 'Administrator'),
        ('staff', 'Staff'),
    )

    DEPARTMENTS = (
        ('cs', 'Computer Science'),
        ('it', 'Information Technology'),
        ('ec', 'Electronics & Communication'),
        ('me', 'Mechanical Engineering'),
        ('ce', 'Civil Engineering'),
        ('admin', 'Administration')
    )
    
    role = models.CharField(max_length=20, choices=ROLES)
    department = models.CharField(max_length=100, choices=DEPARTMENTS)
    student_id = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    linkedin_profile = models.URLField(max_length=200, blank=True)
    github_profile = models.URLField(max_length=200, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)

    # Add related_name to resolve the clash
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    health_requests = models.TextField(blank=True)  # Field to store health requests
    leave_requests = models.TextField(blank=True)    # Field to store leave requests

    def __str__(self):
        return f"{self.username} - {self.role}"

    class Meta:
        permissions = [
            ("can_view_dashboard", "Can view dashboard"),
            ("can_manage_elections", "Can manage elections"),
            ("can_manage_facilities", "Can manage facilities"),
            ("can_handle_complaints", "Can handle complaints"),
        ]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

class HealthRecord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    condition = models.TextField()
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_health_records')
    date_reported = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # If new record
            # Send email notification
            self.send_notification()
        super().save(*args, **kwargs)
    
    def send_notification(self):
        # Implementation for sending email to class coordinator
        pass

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    github_profile = models.URLField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)