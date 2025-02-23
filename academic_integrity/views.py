from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import CheatingCase, Sanction, Appeal
from .forms import CheatingCaseForm, SanctionForm, AppealForm, CaseUpdateForm

@login_required
def case_list(request):
    # Allow access based on role instead of specific permission
    if request.user.is_superuser or 'faculty' in request.user.role:
        cases = CheatingCase.objects.all()
        if not request.user.is_superuser:
            cases = cases.filter(
                Q(reported_by=request.user) | 
                Q(student__department=request.user.department)
            )
    elif request.user.role == 'student':
        cases = CheatingCase.objects.filter(student=request.user)
    else:
        messages.error(request, 'You do not have permission to view cases.')
        return redirect('accounts:dashboard')
    
    return render(request, 'academic_integrity/case_list.html', {'cases': cases})

@login_required
def report_case(request):
    # Only allow faculty to report cases
    if not ('faculty' in request.user.role or request.user.is_superuser):
        messages.error(request, 'Only faculty members can report cases.')
        return redirect('academic_integrity:case_list')

    if request.method == 'POST':
        form = CheatingCaseForm(request.POST, request.FILES)
        if form.is_valid():
            case = form.save(commit=False)
            case.reported_by = request.user
            case.save()
            messages.success(request, 'Case reported successfully.')
            return redirect('academic_integrity:case_detail', pk=case.pk)
    else:
        form = CheatingCaseForm()
    return render(request, 'academic_integrity/report_case.html', {'form': form})

@login_required
def case_detail(request, pk):
    case = get_object_or_404(CheatingCase, pk=pk)
    
    # Check if user has permission to view this case
    if not (request.user.is_superuser or 
            'faculty' in request.user.role or 
            request.user == case.student or 
            request.user == case.reported_by):
        messages.error(request, 'You do not have permission to view this case.')
        return redirect('academic_integrity:case_list')
    
    sanctions = case.sanctions.all()
    appeals = case.appeals.all()
    
    context = {
        'case': case,
        'sanctions': sanctions,
        'appeals': appeals,
    }
    return render(request, 'academic_integrity/case_detail.html', context)

@login_required
def add_sanction(request, case_pk):
    # Only allow faculty to add sanctions
    if not ('faculty' in request.user.role or request.user.is_superuser):
        messages.error(request, 'Only faculty members can add sanctions.')
        return redirect('academic_integrity:case_list')

    case = get_object_or_404(CheatingCase, pk=case_pk)
    if request.method == 'POST':
        form = SanctionForm(request.POST)
        if form.is_valid():
            sanction = form.save(commit=False)
            sanction.case = case
            sanction.issued_by = request.user
            sanction.save()
            messages.success(request, 'Sanction added successfully.')
            return redirect('academic_integrity:case_detail', pk=case_pk)
    else:
        form = SanctionForm()
    return render(request, 'academic_integrity/add_sanction.html', {
        'form': form,
        'case': case
    })

@login_required
def submit_appeal(request, case_pk):
    case = get_object_or_404(CheatingCase, pk=case_pk)
    if request.user != case.student:
        messages.error(request, 'You can only appeal your own cases.')
        return redirect('academic_integrity:case_list')
    
    if case.status == 'closed':
        messages.error(request, 'Cannot appeal a closed case.')
        return redirect('academic_integrity:case_detail', pk=case_pk)
    
    if request.method == 'POST':
        form = AppealForm(request.POST, request.FILES)
        if form.is_valid():
            appeal = form.save(commit=False)
            appeal.case = case
            appeal.submitted_by = request.user
            appeal.save()
            # Update case status to appealed
            case.status = 'appealed'
            case.save()
            messages.success(request, 'Appeal submitted successfully.')
            return redirect('academic_integrity:case_detail', pk=case_pk)
    else:
        form = AppealForm()
    return render(request, 'academic_integrity/submit_appeal.html', {
        'form': form,
        'case': case
    })

@login_required
def update_case(request, pk):
    # Only allow faculty to update cases
    if not ('faculty' in request.user.role or request.user.is_superuser):
        messages.error(request, 'Only faculty members can update cases.')
        return redirect('academic_integrity:case_list')

    case = get_object_or_404(CheatingCase, pk=pk)
    if request.method == 'POST':
        form = CaseUpdateForm(request.POST, instance=case)
        if form.is_valid():
            case = form.save(commit=False)
            if case.status in ['resolved', 'closed']:
                case.resolution_date = timezone.now()
            case.save()
            messages.success(request, 'Case updated successfully.')
            return redirect('academic_integrity:case_detail', pk=pk)
    else:
        form = CaseUpdateForm(instance=case)
    return render(request, 'academic_integrity/update_case.html', {
        'form': form,
        'case': case
    })