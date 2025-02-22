from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from django.db.models import Count
from .forms import UserRegistrationForm, UserUpdateForm, HealthRequestForm, LeaveRequestForm
from elections.models import Election, Nomination, Vote
from complaints.models import Complaint
from facilities.models import Booking
from .models import User
from django.utils import timezone
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView as AuthLoginView, PasswordChangeView as AuthPasswordChangeView, PasswordChangeDoneView as AuthPasswordChangeDoneView
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

class LoginView(AuthLoginView):
    template_name = 'accounts/login.html'  # Specify your login template


@login_required
def dashboard(request):
    """
    Dashboard view that handles both regular and faculty users
    """
    user = request.user
    context = {
        'user': user,
    }
    
    # Check if user is faculty and route to appropriate dashboard
    if user.role == 'faculty-sports':
        # Add sports faculty specific context
        pending_bookings = Booking.objects.filter(status='pending')
        context.update({
            'pending_bookings': pending_bookings,
            'total_pending': pending_bookings.count()
        })
        return render(request, 'accounts/faculty_sports_dashboard.html', context)
    elif user.role == 'faculty-lab':
        return render(request, 'accounts/faculty_lab_dashboard.html', context)
    elif user.role == 'faculty-transport':
        return render(request, 'accounts/faculty_transport_dashboard.html', context)
    elif user.role == 'faculty-hod':
        return render(request, 'accounts/faculty_hod_dashboard.html', context)
    elif user.role == 'faculty-teaching':
        return render(request, 'accounts/faculty_teaching_dashboard.html', context)
    
    # Regular dashboard for non-faculty users
    return render(request, 'accounts/dashboard.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    # Fetch user's complaints including anonymous ones
    complaints = Complaint.objects.filter(
        models.Q(user=request.user) | models.Q(is_anonymous=True, user__isnull=True)
    ).order_by('-created_at')
    
    # Fetch other forms for health and leave requests
    health_form = HealthRequestForm(instance=request.user)
    leave_form = LeaveRequestForm(instance=request.user)

    # Get active elections and user nominations
    active_elections = Election.objects.filter(
        is_active=True,
        nomination_end_date__gte=timezone.now()
    ).order_by('nomination_end_date')
    
    user_nominations = {
        nom.election_id: nom 
        for nom in Nomination.objects.filter(user=request.user)
    }
    
    context = {
        'form': form,
        'health_form': health_form,
        'leave_form': leave_form,
        'complaints': complaints,
        'recent_activities': get_user_activities(request.user),
        'active_elections': active_elections,
        'user_nominations': user_nominations,
        'user': request.user,
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
    if request.method == 'POST':
        logout(request)  # Log the user out
        return redirect('accounts:login')  # Redirect to the login page
    return render(request, 'accounts/logout_confirmation.html')  # Render confirmation template

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
def manage_lab_assignments(request):
    # Logic for managing lab assignments
    return render(request, 'accounts/faculty_lab_dashboard.html', {})

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