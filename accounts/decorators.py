from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def faculty_sports_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'faculty-sports':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Faculty sports privileges required.')
        return redirect('accounts:dashboard')
    return wrapper

def faculty_lab_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'faculty-lab':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Faculty lab privileges required.')
        return redirect('accounts:dashboard')
    return wrapper

def faculty_transport_required(view_func):
    return user_passes_test(lambda u: u.role == 'faculty-transport')(view_func)

def faculty_hod_required(view_func):
    return user_passes_test(lambda u: u.role == 'faculty-hod')(view_func)

def faculty_teaching_required(view_func):
    return user_passes_test(lambda u: u.role == 'faculty-teaching')(view_func)

def is_admin(user):
    return user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html') 