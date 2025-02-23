from django.db import models
from django.conf import settings
from accounts.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ('lab', 'Laboratory'),
        ('sports', 'Sports'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='lab'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_anonymous = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} - {self.user.username if self.user else 'Anonymous'}"

    def get_user_display(self):
        return "Anonymous" if self.is_anonymous else self.user.get_full_name()

    def clean(self):
        # Only validate if the complaint is being created (not updated)
        if not self.pk:  # New complaint
            if self.status == 'resolved' and not self.user:
                raise ValidationError("A user must be assigned to resolve the complaint.")
        # Allow existing complaints to be updated without requiring a user

    class Meta:
        ordering = ['-created_at']

class ComplaintResponse(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    responder = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Response(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Response to {self.complaint.title} by {self.user.username}"