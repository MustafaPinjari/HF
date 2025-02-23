from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver
import datetime
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )
    
    DEPARTMENT_CHOICES = (
        ('CSE', 'Computer Science'),
        ('ECE', 'Electronics'),
        ('ME', 'Mechanical'),
        ('CE', 'Civil'),
    )
    
    DIVISION_CHOICES = (
        ('A', 'Division A'),
        ('B', 'Division B'),
        ('C', 'Division C'),
    )
    
    CLASS_YEAR_CHOICES = (
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    division = models.CharField(max_length=1, choices=DIVISION_CHOICES, blank=True, null=True)
    class_year = models.CharField(max_length=1, choices=CLASS_YEAR_CHOICES, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    student_id = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=15)
    bio = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    linkedin_profile = models.URLField(max_length=200, blank=True)
    github_profile = models.URLField(max_length=200, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    prn = models.CharField(max_length=20, unique=True, null=True, blank=True)

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
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def get_gpa(self):
        enrollments = self.enrollments.filter(grade_points__isnull=False)
        if not enrollments.exists():
            return 0.0
        
        total_points = sum(
            enrollment.grade_points * enrollment.course.credits 
            for enrollment in enrollments
        )
        total_credits = sum(
            enrollment.course.credits 
            for enrollment in enrollments
        )
        
        return round(float(total_points / total_credits), 2)

    def get_attendance_percentage(self, course=None):
        attendance_query = self.attendances.all()
        if course:
            attendance_query = attendance_query.filter(course=course)
        
        total_classes = attendance_query.count()
        if total_classes == 0:
            return 0
        
        attended_classes = attendance_query.filter(is_present=True).count()
        return round((attended_classes / total_classes) * 100, 1)

    def get_enrolled_courses(self, current_only=True):
        enrollments = self.enrollments.all()
        if current_only:
            latest_enrollment = enrollments.order_by('-year', '-semester').first()
            if latest_enrollment:
                enrollments = enrollments.filter(
                    year=latest_enrollment.year,
                    semester=latest_enrollment.semester
                )
        return [enrollment.course for enrollment in enrollments]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @staticmethod
    def generate_prn(admission_year, division, role_number):
        """
        Generate PRN with format: YYYYDDNNN
        YYYY: Admission year
        DD: Division code (01, 02, 03)
        NNN: Role number (padded to 3 digits)
        """
        div_code = dict(User.DIVISION_CHOICES)[division]
        return f"{admission_year}{div_code}{str(role_number).zfill(3)}"

    def clean(self):
        """
        Remove PRN validation since it's auto-generated
        """
        super().clean()
        if self.role == 'student':
            if not self.division:
                raise ValidationError("Division is required for students")
            if not self.class_year:
                raise ValidationError("Class year is required for students")
            # Remove the PRN validation since it's auto-generated

    def save(self, *args, **kwargs):
        """
        Generate PRN for students if not exists
        """
        if self.role == 'student':
            if not self.division:
                raise ValueError("Division is required for students")
            if not self.class_year:
                raise ValueError("Class year is required for students")
            
            # Only generate PRN if it doesn't exist
            if not self.prn:
                try:
                    # Get current year for new students
                    current_year = datetime.datetime.now().year
                    
                    # Get the latest role number for this year and division
                    latest_user = User.objects.filter(
                        prn__startswith=f"{current_year}{dict(User.DIVISION_CHOICES)[self.division]}"
                    ).order_by('-prn').first()
                    
                    if latest_user:
                        # Extract the role number and increment it
                        latest_role_number = int(latest_user.prn[-3:])
                        new_role_number = latest_role_number + 1
                    else:
                        # Start with role number 1
                        new_role_number = 1
                    
                    # Generate the new PRN
                    self.prn = self.generate_prn(current_year, self.division, new_role_number)
                except Exception as e:
                    raise ValueError(f"Error generating PRN: {str(e)}")
        
        super().save(*args, **kwargs)

class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    credits = models.PositiveIntegerField()
    department = models.CharField(max_length=50, choices=User.DEPARTMENT_CHOICES)
    semester = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code']

class Enrollment(models.Model):
    GRADE_CHOICES = (
        ('A+', 'A+'),
        ('A', 'A'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('B-', 'B-'),
        ('C+', 'C+'),
        ('C', 'C'),
        ('C-', 'C-'),
        ('D+', 'D+'),
        ('D', 'D'),
        ('F', 'F'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    year = models.PositiveIntegerField()
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, null=True)
    grade_points = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'course', 'semester', 'year']
    
    def calculate_grade_points(self):
        grade_point_map = {
            'A+': Decimal('4.00'),
            'A': Decimal('4.00'),
            'A-': Decimal('3.70'),
            'B+': Decimal('3.30'),
            'B': Decimal('3.00'),
            'B-': Decimal('2.70'),
            'C+': Decimal('2.30'),
            'C': Decimal('2.00'),
            'C-': Decimal('1.70'),
            'D+': Decimal('1.30'),
            'D': Decimal('1.00'),
            'F': Decimal('0.00'),
        }
        return grade_point_map.get(self.grade, Decimal('0.00'))
    
    def save(self, *args, **kwargs):
        if self.grade:
            self.grade_points = self.calculate_grade_points()
        super().save(*args, **kwargs)

class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['student', 'course', 'date']

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

class Complaint(models.Model):
    CATEGORIES = (
        ('academic', 'Academic'),
        ('infrastructure', 'Infrastructure'),
        ('faculty', 'Faculty'),
        ('lab', 'Laboratory'),
        ('sports', 'Sports'),
        ('transport', 'Transport'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORIES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} - {self.get_status_display()}"

    class Meta:
        ordering = ['-created_at']

class LeaveRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leave_requests_submitted')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_date = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leave_requests_reviewed'
    )
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-submitted_date']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.start_date} to {self.end_date}"