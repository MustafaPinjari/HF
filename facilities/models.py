from django.db import models
from accounts.models import User
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

class Facility(models.Model):
    FACILITY_TYPES = [
        ('sports', 'Sports Facility'),
        ('lab', 'Laboratory'),
        ('transport', 'Transport'),
        ('classroom', 'Classroom'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    capacity = models.IntegerField()
    location = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='facilities/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    type = models.CharField(max_length=20, choices=FACILITY_TYPES, default='other')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_facilities'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Facilities"

    def __str__(self):
        return self.name

    def is_available_for_booking(self, start_time, end_time):
        bookings = Booking.objects.filter(facility=self, status='approved')
        for booking in bookings:
            if (start_time < booking.end_time and end_time > booking.start_time):
                return False
        return self.is_available

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    admin_comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.facility} ({self.status})"

class Course(models.Model):
    title = models.CharField(max_length=200)
    syllabus = models.TextField()
    credits = models.IntegerField()
    department = models.CharField(max_length=100)
    image = models.ImageField(upload_to='courses/', null=True, blank=True)

    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    sponsor = models.CharField(max_length=200)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    expenses = models.DecimalField(max_digits=10, decimal_places=2)
    sponsorship_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    utilization_details = models.TextField(blank=True, null=True)
    expense_proof = models.FileField(upload_to='expense_proofs/', blank=True, null=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_utilization_lines(self):
        if self.utilization_details:
            return self.utilization_details.split('\n')
        return []

    def __str__(self):
        return self.title

class LibraryResource(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=100)
    availability = models.BooleanField(default=True)
    pdf_url = models.URLField(blank=True, null=True)  # Add this line for PDF URL

    def __str__(self):
        return self.title

class CareerService(models.Model):
    description = models.TextField()

    def __str__(self):
        return "Career Services"

class SupportService(models.Model):
    description = models.TextField()

    def __str__(self):
        return "Support Services"

class ExtracurricularActivity(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name

class Alumni(models.Model):
    name = models.CharField(max_length=200)
    graduation_year = models.IntegerField()
    linkedin_profile = models.URLField(blank=True)

    def __str__(self):
        return self.name

class TransportFacility(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    capacity = models.IntegerField()
    image = models.ImageField(upload_to='transport/', null=True, blank=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publication_year = models.IntegerField(null=True, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    book_link = models.URLField(max_length=500, null=True, blank=True)
    available_copies = models.IntegerField(default=1)
    total_copies = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.title} by {self.author}"

    @property
    def is_available(self):
        return self.available_copies > 0

class BookRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.due_date:
            self.due_date = timezone.now().date() + timezone.timedelta(days=14)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    def calculate_fine(self):
        if self.status == 'returned' and self.return_date > self.due_date:
            days_late = (self.return_date - self.due_date).days
            self.fine_amount = days_late * 1  # $1 per day late
            self.save()