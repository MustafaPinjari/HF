from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from django.db.models import Count
from .forms import (
    StudentRegistrationForm, 
    FacultyRegistrationForm, 
    AdminRegistrationForm,
    UserUpdateForm,
    HealthRequestForm,
    LeaveRequestForm,
    CourseForm,
    BulkAttendanceForm,
    EnrollmentForm,
    GradeUpdateForm,
    AttendanceForm
)
from elections.models import Election, Nomination, Vote
from complaints.models import Complaint
from facilities.models import Booking, Book, BookRequest, Facility
from .models import User, LeaveRequest, HealthRecord, Course, Enrollment, Attendance
from django.utils import timezone
from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import PasswordChangeView as AuthPasswordChangeView, PasswordChangeDoneView as AuthPasswordChangeDoneView
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from .decorators import (
    faculty_sports_required,
    faculty_lab_required,
    faculty_transport_required,
    faculty_hod_required,
    faculty_teaching_required
)
from django.views.generic import TemplateView
from .utils import get_dashboard_url
from datetime import timedelta
import json
from django.urls import reverse_lazy
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from academic_integrity.models import CheatingCase

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('accounts:dashboard')
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        try:
            response = super().form_valid(form)
            messages.success(self.request, f'Welcome back, {self.request.user.get_full_name() or self.request.user.username}!')
            return response
        except ValueError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        if self.request.user.role == 'admin':
            return reverse_lazy('accounts:admin_dashboard')
        return super().get_success_url()

@login_required
def dashboard(request):
    """Route users to their appropriate dashboard based on their role"""
    role_dashboard_mapping = {
        'admin': 'accounts:admin_dashboard',
        'faculty-sports': 'accounts:faculty_sports_dashboard',
        'faculty-lab': 'accounts:faculty_lab_dashboard',
        'faculty-transport': 'accounts:faculty_transport_dashboard',
        'faculty-hod': 'accounts:faculty_hod_dashboard',
        'faculty-teaching': 'accounts:faculty_teaching_dashboard',
    }

    if request.user.role in role_dashboard_mapping:
        return redirect(role_dashboard_mapping[request.user.role])
    
    # Default student dashboard
    context = {
        'user': request.user,
        # Add other context data for student dashboard
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
@faculty_sports_required
def faculty_sports_dashboard(request):
    context = {
        'pending_bookings': SportsFacilityBooking.objects.filter(status='pending'),
        'total_pending': SportsFacilityBooking.objects.filter(status='pending').count(),
        # Add other sports faculty specific context
    }
    return render(request, 'accounts/faculty_sports_dashboard.html', context)

@login_required
@faculty_lab_required
def faculty_lab_dashboard(request):
    context = {
        'book_requests': LabBookRequest.objects.filter(status='pending'),
        'lab_complaints': LabComplaint.objects.filter(status='pending'),
        'total_pending_books': LabBookRequest.objects.filter(status='pending').count(),
        # Add other lab faculty specific context
    }
    return render(request, 'accounts/faculty_lab_dashboard.html', context)

@login_required
@faculty_transport_required
def faculty_transport_dashboard(request):
    context = {
        'transport_requests': TransportRequest.objects.filter(status='pending'),
        'vehicle_status': VehicleStatus.objects.all(),
        # Add other transport faculty specific context
    }
    return render(request, 'accounts/faculty_transport_dashboard.html', context)

@login_required
@faculty_hod_required
def faculty_hod_dashboard(request):
    department = request.user.department
    context = {
        'department_students': User.objects.filter(department=department, role='student'),
        'department_faculty': User.objects.filter(department=department, role__startswith='faculty'),
        'department_complaints': Complaint.objects.filter(user__department=department),
        # Add other HOD specific context
    }
    return render(request, 'accounts/faculty_hod_dashboard.html', context)

@login_required
@faculty_teaching_required
def faculty_teaching_dashboard(request):
    context = {
        'students': User.objects.filter(role='student', department=request.user.department),
        'cheating_cases': CheatingCase.objects.filter(reported_by=request.user),
        'health_records': HealthRecord.objects.filter(student__department=request.user.department),
        # Remove the line with LeaveRequest since we haven't implemented it yet
    }
    return render(request, 'accounts/faculty_teaching_dashboard.html', context)

@login_required
def student_dashboard(request):
    context = {
        'active_elections': Election.objects.filter(is_active=True),
        'recent_complaints': request.user.complaints.all()[:5],
        'user_bookings': Booking.objects.filter(user=request.user, status='approved'),
        'live_results': get_live_election_results(),
        # Add other student specific context
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def admin_dashboard(request):
    """
    Admin dashboard view showing system statistics and management options
    """
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:dashboard')

    # Get statistics for the dashboard
    context = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_faculty': User.objects.filter(role__startswith='faculty-').count(),
        'active_complaints': Complaint.objects.filter(status__in=['pending', 'in_progress']).count(),
        
        # Recent activities (last 7 days)
        'recent_activities': get_recent_activities(),
        
        # System health metrics (example values)
        'server_health': 95,
        'database_health': 98,
        
        # Chart data (last 7 days)
        'chart_labels': json.dumps([d.strftime('%Y-%m-%d') for d in get_last_7_days()]),
        'chart_data': get_user_activity_data(),
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
def broadcast_announcement(request):
    """
    Handle broadcast announcements from admin dashboard
    """
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        audience = request.POST.get('audience')
        
        # Here you would implement the actual announcement broadcasting
        # For example, create an Announcement model instance
        
        messages.success(request, 'Announcement broadcast successfully.')
        return redirect('accounts:admin_dashboard')

    return redirect('accounts:admin_dashboard')

# Helper functions for dashboard data
def get_last_7_days():
    """Helper function to get dates for the last 7 days"""
    today = timezone.now()
    return [(today - timedelta(days=i)) for i in range(6, -1, -1)]

def get_user_activity_data():
    """Helper function to get user activity data for the chart"""
    dates = get_last_7_days()
    return [User.objects.filter(last_login__date=date.date()).count() for date in dates]

def get_recent_activities():
    """Helper function to get recent system activities"""
    last_week = timezone.now() - timedelta(days=7)
    activities = []
    
    # Add recent user registrations
    new_users = User.objects.filter(date_joined__gte=last_week)
    for user in new_users:
        activities.append({
            'type': 'registration',
            'description': f'New user registered: {user.get_full_name()}',
            'timestamp': user.date_joined
        })
    
    # Add recent complaints
    recent_complaints = Complaint.objects.filter(created_at__gte=last_week)
    for complaint in recent_complaints:
        activities.append({
            'type': 'complaint',
            'description': f'New complaint filed: {complaint.subject}',
            'timestamp': complaint.created_at
        })
    
    # Sort activities by timestamp and return the 10 most recent
    return sorted(activities, key=lambda x: x['timestamp'], reverse=True)[:10]

def role_selection(request):
    return render(request, 'accounts/role_selection.html')

def register(request, role):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    form_classes = {
        'student': StudentRegistrationForm,
        'faculty': FacultyRegistrationForm,
        'admin': AdminRegistrationForm
    }

    FormClass = form_classes.get(role)
    if not FormClass:
        return redirect('accounts:role_selection')

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = FormClass()

    return render(request, 'accounts/register.html', {
        'form': form,
        'role': role
    })

@login_required
def profile(request):
    form = UserUpdateForm(instance=request.user)
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            # Handle profile update
            form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                user = form.save(commit=False)
                if user.linkedin_profile and not user.linkedin_profile.startswith(('http://', 'https://')):
                    user.linkedin_profile = f'https://{user.linkedin_profile}'
                if user.github_profile and not user.github_profile.startswith(('http://', 'https://')):
                    user.github_profile = f'https://{user.github_profile}'
                user.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('accounts:profile')
        
        elif 'submit_complaint' in request.POST:
            try:
                # Create new complaint with correct field names
                new_complaint = Complaint(
                    user=request.user,
                    subject=request.POST.get('complaint_subject'),  # These field names match the model
                    description=request.POST.get('complaint_description'),
                    category=request.POST.get('complaint_category'),
                    status='pending'  # Set default status
                )
                new_complaint.save()  # Save the complaint
                messages.success(request, 'Complaint submitted successfully!')
            except Exception as e:
                messages.error(request, f'Error submitting complaint: {str(e)}')
            return redirect('accounts:profile')
    
    # Get user's complaints ordered by most recent first
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'form': form,
        'complaints': complaints,
    }
    return render(request, 'accounts/profile.html', context)

def get_user_activities(user):
    """Get recent activities for the user across all modules"""
    activities = []
    
    try:
        # Add elections activity - check if Vote model exists
        activities.extend(Election.objects.filter(vote__user=user).distinct().order_by('-created_at')[:5])
    except (ImportError, AttributeError):
        # Skip if Vote model or related field doesn't exist
        pass

    try:
        # Add complaints activity
        activities.extend(Complaint.objects.filter(user=user).order_by('-created_at')[:5])
    except Exception:
        pass

    try:
        # Add bookings activity
        activities.extend(Booking.objects.filter(user=user).order_by('-created_at')[:5])
    except Exception:
        pass
    
    # Filter out activities without created_at and sort
    valid_activities = [a for a in activities if hasattr(a, 'created_at')]
    return sorted(valid_activities, key=lambda x: x.created_at, reverse=True)[:10]

def logout_confirmation(request):
    return render(request, 'accounts/logout_confirmation.html')

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('accounts:login')
    return redirect('accounts:logout_confirmation')

@login_required
def submit_health_request(request):
    if request.method == 'POST':
        form = HealthRequestForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Health request submitted successfully!')
            return redirect('accounts:profile')
    else:
        form = HealthRequestForm(instance=request.user)
    return render(request, 'accounts/submit_health_request.html', {'form': form})

@login_required
def submit_leave_request(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave request submitted successfully!')
            return redirect('accounts:profile')
    else:
        form = LeaveRequestForm(instance=request.user)
    return render(request, 'accounts/submit_leave_request.html', {'form': form})

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.department = request.POST.get('department')
        user.bio = request.POST.get('bio')
        user.linkedin_profile = request.POST.get('linkedin_profile')
        user.github_profile = request.POST.get('github_profile')

        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']

        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
@faculty_sports_required
def approve_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        action = request.POST.get('action')
        
        if action == 'approve':
            booking.status = 'approved'
            notification_message = f"Your booking for {booking.facility.name} on {booking.start_time.date()} has been approved."
        elif action == 'reject':
            booking.status = 'rejected'
            notification_message = f"Your booking for {booking.facility.name} on {booking.start_time.date()} has been rejected."
        
        booking.save()
        
        # Send email notification
        send_mail(
            subject=f'Facility Booking {booking.status.title()}',
            message=notification_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=True,
        )
        
        # Add success message
        messages.success(request, f'Booking has been {booking.status}')
        
        # Redirect back to the dashboard
        return redirect('accounts:dashboard')
        
    except Booking.DoesNotExist:
        messages.error(request, 'Booking not found')
        return redirect('accounts:dashboard')

@login_required
@faculty_lab_required
def handle_book_request(request, request_id):
    try:
        book_request = BookRequest.objects.get(id=request_id)
        status = request.POST.get('status')
        
        if status in ['approved', 'rejected']:
            book_request.status = status
            book_request.save()
            
            # Update book availability if request is approved
            if status == 'approved':
                book = book_request.book
                book.available_copies -= 1
                book.save()
            
            # Send notification to user
            notification_message = f"Your request for '{book_request.book.title}' has been {status}."
            send_mail(
                subject=f'Book Request {status.title()}',
                message=notification_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[book_request.user.email],
                fail_silently=True,
            )
            
            messages.success(request, f'Book request has been {status}')
        
        return redirect('accounts:dashboard')
        
    except BookRequest.DoesNotExist:
        messages.error(request, 'Book request not found')
        return redirect('accounts:dashboard')

@login_required
@faculty_lab_required
def handle_lab_complaint(request, complaint_id):
    try:
        complaint = Complaint.objects.get(id=complaint_id, category='lab')
        status = request.POST.get('status')
        
        if status in ['in_progress', 'resolved']:
            complaint.status = status
            complaint.save()
            
            # Send notification to user
            notification_message = f"Your lab complaint '{complaint.title}' is now {status}."
            send_mail(
                subject=f'Lab Complaint Update',
                message=notification_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[complaint.user.email],
                fail_silently=True,
            )
            
            messages.success(request, f'Complaint status updated to {status}')
        
        return redirect('accounts:dashboard')
        
    except Complaint.DoesNotExist:
        messages.error(request, 'Complaint not found')
        return redirect('accounts:dashboard')

@login_required
@faculty_transport_required
def assign_transport(request):
    # Logic for assigning transport
    return render(request, 'accounts/faculty_transport_dashboard.html', {})

@login_required
@faculty_hod_required
def track_users(request):
    # Logic for tracking users and complaints
    return render(request, 'accounts/faculty_hod_dashboard.html', {})

@login_required
@faculty_teaching_required
def manage_leave_requests(request):
    # Logic for managing leave requests
    return render(request, 'accounts/faculty_teaching_dashboard.html', {})

@login_required
@faculty_teaching_required
def review_leave_request(request, request_id):
    leave_request = get_object_or_404(LeaveRequest, id=request_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if status in ['approved', 'rejected']:
            leave_request.status = status
            leave_request.review_notes = notes
            leave_request.reviewed_by = request.user
            leave_request.review_date = timezone.now()
            leave_request.save()
            
            messages.success(request, f'Leave request {status}.')
            return redirect('accounts:faculty_teaching_dashboard')
    
    return render(request, 'accounts/review_leave_request.html', {
        'leave_request': leave_request
    })

def home(request):
    """
    Redirect to appropriate dashboard if user is authenticated,
    otherwise redirect to login page
    """
    if request.user.is_authenticated:
        dashboard_url = get_dashboard_url(request.user)
        return redirect(dashboard_url)
    return redirect('accounts:login')

@login_required
def student_profile(request, username):
    student = get_object_or_404(User, username=username, role='student')
    
    # Check if the user has permission to view this profile
    if not (request.user.is_superuser or 
            (request.user.role == 'faculty' and student.department == request.user.department) or 
            request.user == student):
        messages.error(request, "You don't have permission to view this profile.")
        return redirect('accounts:dashboard')
    
    context = {
        'student': student,
        'health_records': HealthRecord.objects.filter(student=student),
        'cheating_cases': CheatingCase.objects.filter(student=student),
        'academic_performance': {
            'gpa': student.get_gpa(),
            'attendance': student.get_attendance_percentage(),
            'courses': student.get_enrolled_courses(),
        }
    }
    return render(request, 'accounts/student_profile.html', context)

# Add these helper methods to the User model in accounts/models.py
def get_gpa(self):
    # Placeholder method - implement actual GPA calculation
    return 3.5

def get_attendance_percentage(self):
    # Placeholder method - implement actual attendance calculation
    return 85

def get_enrolled_courses(self):
    # Placeholder method - implement actual course enrollment
    return ['Course 1', 'Course 2', 'Course 3']

@login_required
def course_list(request):
    if request.user.role == 'faculty':
        courses = Course.objects.filter(department=request.user.department)
    elif request.user.role == 'student':
        courses = Course.objects.filter(
            enrollment__student=request.user
        ).distinct()
    else:
        courses = Course.objects.none()
    
    return render(request, 'accounts/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check permissions
    if request.user.role == 'student':
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.error(request, "You are not enrolled in this course.")
            return redirect('accounts:course_list')
    elif request.user.role == 'faculty':
        if course.department != request.user.department:
            messages.error(request, "You don't have access to this course.")
            return redirect('accounts:course_list')
    
    context = {
        'course': course,
        'enrollments': Enrollment.objects.filter(course=course),
        'attendance_records': Attendance.objects.filter(course=course)
    }
    return render(request, 'accounts/course_detail.html', context)

@login_required
@faculty_teaching_required
def manage_course(request, course_id=None):
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        if course.department != request.user.department:
            messages.error(request, "You don't have permission to edit this course.")
            return redirect('accounts:course_list')
    else:
        course = None
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save(commit=False)
            course.department = request.user.department
            course.save()
            messages.success(request, 'Course saved successfully.')
            return redirect('accounts:course_list')
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'accounts/manage_course.html', {
        'form': form,
        'course': course
    })

@login_required
@faculty_teaching_required
def mark_attendance(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.department != request.user.department:
        messages.error(request, "You don't have permission to mark attendance for this course.")
        return redirect('accounts:course_list')
    
    students = User.objects.filter(
        enrollments__course=course,
        role='student'
    )
    
    if request.method == 'POST':
        form = BulkAttendanceForm(request.POST, students=students)
        if form.is_valid():
            date = form.cleaned_data['date']
            for student in students:
                is_present = form.cleaned_data[f'student_{student.id}']
                Attendance.objects.update_or_create(
                    student=student,
                    course=course,
                    date=date,
                    defaults={'is_present': is_present}
                )
            messages.success(request, 'Attendance marked successfully.')
            return redirect('accounts:course_detail', course_id=course_id)
    else:
        form = BulkAttendanceForm(students=students)
    
    return render(request, 'accounts/mark_attendance.html', {
        'form': form,
        'course': course,
        'students': students
    })

@login_required
@faculty_teaching_required
def update_grades(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.department != request.user.department:
        messages.error(request, "You don't have permission to update grades for this course.")
        return redirect('accounts:course_list')
    
    enrollments = Enrollment.objects.filter(course=course)
    
    if request.method == 'POST':
        for enrollment in enrollments:
            grade = request.POST.get(f'grade_{enrollment.id}')
            if grade:
                enrollment.grade = grade
                enrollment.save()
        messages.success(request, 'Grades updated successfully.')
        return redirect('accounts:course_detail', course_id=course_id)
    
    return render(request, 'accounts/update_grades.html', {
        'course': course,
        'enrollments': enrollments
    })

@login_required
def enroll_course(request, course_id):
    if request.user.role != 'student':
        messages.error(request, "Only students can enroll in courses.")
        return redirect('accounts:course_list')
    
    course = get_object_or_404(Course, id=course_id)
    
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, "You are already enrolled in this course.")
        return redirect('accounts:course_list')
    
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = request.user
            enrollment.course = course
            enrollment.save()
            messages.success(request, f'Successfully enrolled in {course.name}')
            return redirect('accounts:course_list')
    else:
        form = EnrollmentForm()
    
    return render(request, 'accounts/enroll_course.html', {
        'form': form,
        'course': course
    })