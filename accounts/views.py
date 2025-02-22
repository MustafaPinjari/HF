from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
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

class LoginView(AuthLoginView):
    template_name = 'accounts/login.html'  # Specify your login template


@login_required
def dashboard(request):
    bookings = Booking.objects.filter(user=request.user)
    live_results = {}
    for election in Election.objects.filter(is_active=True):
        candidates = Nomination.objects.filter(election=election, status='approved')
        candidate_names = [candidate.user.get_full_name() for candidate in candidates]
        vote_count = Vote.objects.filter(election=election).count()
        
        live_results[election.id] = {
            'title': election.title,
            'vote_count': vote_count,
            'candidates': candidate_names,
        }

    context = {
        'active_elections': Election.objects.filter(is_active=True),
        'user_bookings': bookings.order_by('-start_time')[:5],
        'live_results': live_results,
        'recent_complaints': Complaint.objects.filter(user=request.user).order_by('-created_at')[:5],
        'user': request.user  # Ensure user is passed to the context
    }
    
    # Add role-specific data
    if request.user.role in ['admin', 'faculty']:
        context.update({
            'total_students': User.objects.filter(role='student').count(),
            'department_stats': User.objects.filter(role='student').values('department').annotate(count=Count('id')),
            'pending_complaints': Complaint.objects.filter(status='pending').count(),
            'facility_usage': bookings.values('facility__name').annotate(count=Count('id'))
        })
    
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