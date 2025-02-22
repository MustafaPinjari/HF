from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from .models import Facility, Booking, Course, Event, LibraryResource, CareerService, SupportService, ExtracurricularActivity, Alumni, TransportFacility
from .forms import BookingForm, EventForm, FacilityForm
from accounts.decorators import faculty_sports_required

@login_required
def facility_list(request):
    """View for regular users to see and book facilities"""
    facilities = Facility.objects.all()
    return render(request, 'facilities/facility_list.html', {
        'facilities': facilities,
        'is_faculty_sports': request.user.role == 'faculty-sports'
    })

@login_required
@faculty_sports_required
def facility_management(request):
    """View for faculty-sports to manage facilities"""
    facilities = Facility.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        capacity = request.POST.get('capacity')
        location = request.POST.get('location')
        image = request.FILES.get('image')  # Handle image upload
        
        try:
            facility = Facility.objects.create(
                name=name,
                description=description,
                capacity=capacity,
                location=location,
                created_by=request.user
            )
            if image:
                facility.image = image
                facility.save()
            
            messages.success(request, 'Facility created successfully!')
            return redirect('facilities:facility_management')
        except Exception as e:
            messages.error(request, f'Error creating facility: {str(e)}')
    
    return render(request, 'facilities/facility_management.html', {'facilities': facilities})

@login_required
def book_facility(request, facility_id):
    facility = get_object_or_404(Facility, id=facility_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            if facility.is_available_for_booking(start_time, end_time):
                booking = form.save(commit=False)
                booking.user = request.user
                booking.status = 'pending'  # Set initial status to pending
                booking.save()
                return redirect('facilities:my_bookings')  # Redirect to user's bookings
            else:
                messages.error(request, 'The facility is not available for the selected time.')
    else:
        form = BookingForm(initial={'facility': facility})

    return render(request, 'facilities/book_facility.html', {'form': form, 'facility': facility})

@login_required
@permission_required('facilities.can_manage_facilities')
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        booking.status = 'approved'
        booking.save()
        messages.success(request, 'Booking approved successfully!')
        return redirect('facilities:my_bookings')
    return render(request, 'facilities/approve_booking.html', {'booking': booking})

@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        booking.status = 'rejected'
        booking.admin_comments = request.POST.get('admin_comments', '')
        booking.save()
        messages.success(request, 'Booking rejected successfully!')
        return redirect('facilities:my_bookings')
    return render(request, 'facilities/reject_booking.html', {'booking': booking})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'facilities/my_bookings.html', {'bookings': bookings})

@login_required
def admin_bookings(request):
    bookings = Booking.objects.all().order_by('-created_at')
    return render(request, 'facilities/admin_bookings.html', {'bookings': bookings})

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'facilities/course_list.html', {'courses': courses})

@login_required
def event_list(request):
    events = Event.objects.all()
    return render(request, 'facilities/event_list.html', {'events': events})

@login_required
def library_resources(request):
    resources = LibraryResource.objects.all()
    return render(request, 'facilities/library_resources.html', {'resources': resources})

@login_required
def career_services(request):
    services = CareerService.objects.all()
    return render(request, 'facilities/career_services.html', {'services': services})

@login_required
def support_services(request):
    services = SupportService.objects.all()
    return render(request, 'facilities/support_services.html', {'services': services})

@login_required
def extracurricular_activities(request):
    activities = ExtracurricularActivity.objects.all()
    return render(request, 'facilities/extracurricular_activities.html', {'activities': activities})

@login_required
def alumni_network(request):
    alumni = Alumni.objects.all()
    return render(request, 'facilities/alumni_network.html', {'alumni': alumni})

@login_required
def transport_facilities(request):
    transport_facilities = TransportFacility.objects.all()
    return render(request, 'facilities/transport_facilities.html', {'transport_facilities': transport_facilities})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'facilities/event_detail.html', {'event': event})

# Check if the user is an admin
def is_admin(user):
    return user.role == 'admin'  # Adjust this based on your user model

@login_required
@user_passes_test(is_admin)
def pending_bookings(request):
    bookings = Booking.objects.filter(status='pending')
    return render(request, 'facilities/pending_bookings.html', {'bookings': bookings})

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('facilities:event_list')  # Redirect to the event list after saving
    else:
        form = EventForm()
    return render(request, 'facilities/create_event.html', {'form': form})

@login_required
@permission_required('facilities.can_manage_facilities')
def faculty_sports_dashboard(request):
    # Fetch pending bookings for faculty sports
    pending_bookings = Booking.objects.filter(status='pending')
    return render(request, 'facilities/faculty_sports_dashboard.html', {'pending_bookings': pending_bookings})

@login_required
@faculty_sports_required
def manage_facilities(request):
    facilities = Facility.objects.all()
    
    if request.method == 'POST':
        form = FacilityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('facilities:manage_facilities')
    else:
        form = FacilityForm()
    
    return render(request, 'facilities/manage_facilities.html', {
        'facilities': facilities,
        'form': form,
    })