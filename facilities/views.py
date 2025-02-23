from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from .models import Facility, Booking, Course, Event, LibraryResource, CareerService, SupportService, ExtracurricularActivity, Alumni, TransportFacility, Book, BookRequest
from .forms import BookingForm, EventForm, FacilityForm
from accounts.decorators import faculty_sports_required
from datetime import datetime, timedelta
from django.utils import timezone
import csv

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
    books = Book.objects.all().order_by('title')
    min_return_date = timezone.now().date() + timedelta(days=1)
    default_return_date = timezone.now().date() + timedelta(days=14)
    
    # Get user's current book requests
    user_requests = BookRequest.objects.filter(
        user=request.user,
        status__in=['pending', 'approved']
    ).select_related('book')
    
    # Create a set of book IDs that the user has already requested
    requested_books = {req.book.id for req in user_requests}
    
    context = {
        'books': books,
        'min_return_date': min_return_date,
        'default_return_date': default_return_date,
        'requested_books': requested_books,
        'user_requests': user_requests
    }
    return render(request, 'facilities/library_resources.html', context)

@login_required
def import_books_from_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        for row in reader:
            Book.objects.get_or_create(
                isbn=row['isbn'],
                defaults={
                    'title': row['title'],
                    'author': row['author'],
                    'category': row.get('category', ''),
                    'publication_year': row.get('publication_year'),
                    'total_copies': int(row.get('copies', 1)),
                    'available_copies': int(row.get('copies', 1))
                }
            )
        messages.success(request, 'Books imported successfully!')
        return redirect('facilities:book_list')
    return render(request, 'facilities/import_books.html')

@login_required
def book_list(request):
    books = Book.objects.all().order_by('title')
    return render(request, 'facilities/book_list.html', {'books': books})

@login_required
def request_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    # Check if user already has a pending or approved request for this book
    existing_request = BookRequest.objects.filter(
        user=request.user,
        book=book,
        status__in=['pending', 'approved']
    ).exists()
    
    if existing_request:
        messages.error(request, 'You already have an active request for this book.')
        return redirect('facilities:library_resources')
    
    if book.available_copies <= 0:
        messages.error(request, 'This book is currently unavailable.')
        return redirect('facilities:library_resources')
    
    # Create the book request
    BookRequest.objects.create(
        user=request.user,
        book=book,
        status='pending'
    )
    
    messages.success(request, f'Your request for "{book.title}" has been submitted.')
    return redirect('facilities:library_resources')

@login_required
def my_books(request):
    book_requests = BookRequest.objects.filter(user=request.user).order_by('-request_date')
    return render(request, 'facilities/my_books.html', {'book_requests': book_requests})

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