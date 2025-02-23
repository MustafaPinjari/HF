from django.db import models
from django.conf import settings
from django.utils import timezone

class CheatingCase(models.Model):
    CASE_STATUS = (
        ('pending', 'Pending Review'),
        ('under_investigation', 'Under Investigation'),
        ('hearing_scheduled', 'Hearing Scheduled'),
        ('resolved', 'Resolved'),
        ('appealed', 'Under Appeal'),
        ('closed', 'Case Closed'),
    )

    VIOLATION_TYPES = (
        ('exam_cheating', 'Examination Cheating'),
        ('plagiarism', 'Plagiarism'),
        ('impersonation', 'Impersonation'),
        ('unauthorized_materials', 'Unauthorized Materials'),
        ('electronic_device', 'Electronic Device Usage'),
        ('collusion', 'Collusion'),
        ('other', 'Other'),
    )

    SEVERITY_LEVELS = (
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('severe', 'Severe'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='cheating_cases'
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='reported_cases'
    )
    course = models.CharField(max_length=100)
    exam_date = models.DateField()
    violation_type = models.CharField(max_length=50, choices=VIOLATION_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    description = models.TextField()
    evidence = models.FileField(upload_to='cheating_evidence/', blank=True)
    status = models.CharField(max_length=20, choices=CASE_STATUS, default='pending')
    date_reported = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    resolution_date = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_reported']
        permissions = [
            ("can_view_all_cases", "Can view all cheating cases"),
            ("can_manage_cases", "Can manage cheating cases"),
            ("can_resolve_cases", "Can resolve cheating cases"),
        ]

class Sanction(models.Model):
    SANCTION_TYPES = (
        ('warning', 'Written Warning'),
        ('zero_grade', 'Zero Grade in Exam'),
        ('course_failure', 'Course Failure'),
        ('suspension', 'Temporary Suspension'),
        ('expulsion', 'Expulsion'),
        ('other', 'Other'),
    )

    case = models.ForeignKey(CheatingCase, on_delete=models.CASCADE, related_name='sanctions')
    sanction_type = models.CharField(max_length=50, choices=SANCTION_TYPES)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='issued_sanctions'
    )
    date_issued = models.DateTimeField(auto_now_add=True)

class Appeal(models.Model):
    APPEAL_STATUS = (
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    case = models.ForeignKey(CheatingCase, on_delete=models.CASCADE, related_name='appeals')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    submission_date = models.DateTimeField(auto_now_add=True)
    grounds = models.TextField()
    supporting_evidence = models.FileField(upload_to='appeal_evidence/', blank=True)
    status = models.CharField(max_length=20, choices=APPEAL_STATUS, default='pending')
    reviewer_notes = models.TextField(blank=True)
    review_date = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='reviewed_appeals',
        null=True,
        blank=True
    )