from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Complaint, ComplaintResponse
from .forms import ComplaintForm, ResponseForm
from utils.notifications import send_complaint_notification
from django.utils import timezone

@login_required
def complaint_list(request):
    # Fetch all complaints
    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, 'complaints/complaint_list.html', {'complaints': complaints})

@login_required
def add_response(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.complaint = complaint
            response.responder = request.user
            response.save()
            messages.success(request, 'Response added successfully!')
            return redirect('complaints:detail', pk=pk)
    else:
        form = ResponseForm()
    
    return render(request, 'complaints/add_response.html', {
        'form': form,
        'complaint': complaint
    })

@login_required
def create_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            # Assign the user only if the complaint is not anonymous
            if not form.cleaned_data['is_anonymous']:
                complaint.user = request.user  # Assign the logged-in user
            complaint.save()
            messages.success(request, 'Your complaint has been submitted successfully!')
            return redirect('accounts:profile')  # Redirect to the profile page
    else:
        form = ComplaintForm()
    return render(request, 'complaints/create_complaint.html', {'form': form})

@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if complaint.user != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to view this complaint.")
        return redirect('accounts:profile')
    
    responses = complaint.complaintresponse_set.all().order_by('created_at')
    return render(request, 'complaints/complaint_detail.html', {
        'complaint': complaint,
        'responses': responses
    })

@login_required
def submit_complaint(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        
        try:
            # Create the complaint
            complaint = Complaint.objects.create(
                user=None if is_anonymous else request.user,
                title=title,
                description=description,
                is_anonymous=is_anonymous,
                status='pending',
                created_at=timezone.now()
            )
            messages.success(request, 'Complaint submitted successfully!')
        except Exception as e:
            messages.error(request, f'Error submitting complaint: {str(e)}')
        
        return redirect('accounts:profile')
    
    return redirect('accounts:profile')