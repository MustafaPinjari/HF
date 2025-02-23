from django.db import models
from accounts.models import User
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    nomination_start_date = models.DateTimeField()
    nomination_end_date = models.DateTimeField()
    voting_start_date = models.DateTimeField(default=timezone.now)
    voting_end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def is_nomination_open(self):
        now = timezone.now()
        return self.nomination_start_date <= now <= self.nomination_end_date

    @property
    def is_voting_open(self):
        now = timezone.now()
        return self.voting_start_date <= now <= self.voting_end_date

    def __str__(self):
        return self.title

class Nomination(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    )
    
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # This is the candidate
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    manifesto = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='nominations/', blank=True, null=True)
    admin_remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.election.title}"

class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nomination = models.OneToOneField(Nomination, on_delete=models.CASCADE)
    votes_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.election.title}"
    
    class Meta:
        unique_together = ('election', 'user')

class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes_cast')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes_received')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='votes')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('election', 'voter')
        
    def save(self, *args, **kwargs):
        # Increment candidate's vote count when a new vote is cast
        if not self.pk:  # Only for new votes
            self.candidate.votes_count += 1
            self.candidate.save()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.voter.username} voted in {self.election.title}"