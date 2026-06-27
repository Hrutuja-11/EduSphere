from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Company, JobPosting, JobApplication
from .forms import JobPostingForm

@login_required
def browse_jobs(request):
    if request.user.role != 'student':
        messages.error(request, "Only students can browse and apply for jobs.")
        return redirect('dashboard')
        
    student = request.user.student_profile
    active_postings = JobPosting.objects.filter(is_active=True).select_related('company')
    
    # Get IDs of jobs this student has already applied to
    applied_job_ids = JobApplication.objects.filter(student=student).values_list('job_posting_id', flat=True)
    
    # Check eligibility for each posting
    for posting in active_postings:
        posting.is_eligible = student.cgpa >= posting.min_cgpa
        posting.has_applied = posting.id in applied_job_ids
        posting.is_past_deadline = posting.application_deadline < timezone.now().date()
        
    context = {
        'student': student,
        'postings': active_postings,
    }
    return render(request, 'placements/browse_jobs.html', context)


@login_required
def job_detail(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    
    has_applied = False
    is_eligible = False
    is_past_deadline = job.application_deadline < timezone.now().date()
    
    if request.user.role == 'student':
        student = request.user.student_profile
        has_applied = JobApplication.objects.filter(job_posting=job, student=student).exists()
        is_eligible = student.cgpa >= job.min_cgpa
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'is_eligible': is_eligible,
        'is_past_deadline': is_past_deadline,
    }
    return render(request, 'placements/job_detail.html', context)


@login_required
def apply_job(request, job_id):
    if request.user.role != 'student':
        messages.error(request, "Only students can apply for jobs.")
        return redirect('dashboard')
        
    job = get_object_or_404(JobPosting, id=job_id)
    student = request.user.student_profile
    
    # 1. Check if already applied
    if JobApplication.objects.filter(job_posting=job, student=student).exists():
        messages.error(request, "You have already applied for this job.")
        return redirect('job_detail', job_id=job.id)
        
    # 2. Check CGPA eligibility
    if student.cgpa < job.min_cgpa:
        messages.error(request, f"You are not eligible. Your CGPA ({student.cgpa}) is below the required minimum ({job.min_cgpa}).")
        return redirect('job_detail', job_id=job.id)
        
    # 3. Check deadline
    if job.application_deadline < timezone.now().date():
        messages.error(request, "The application deadline for this job has passed.")
        return redirect('job_detail', job_id=job.id)
        
    # Create application
    # Default resume URL points to their public portfolio
    resume_url = request.build_absolute_uri(f"/portfolio/{request.user.username}/")
    
    JobApplication.objects.create(
        job_posting=job,
        student=student,
        resume_url=resume_url,
        status='applied'
    )
    
    messages.success(request, f"Successfully applied for {job.title} at {job.company.name}!")
    return redirect('browse_jobs')


@login_required
def manage_placements(request):
    if request.user.role != 'placement_officer':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    postings = JobPosting.objects.all().select_related('company')
    applications = JobApplication.objects.all().select_related('student__user', 'job_posting__company')
    companies = Company.objects.all()
    job_form = JobPostingForm()
    
    context = {
        'postings': postings,
        'applications': applications,
        'companies': companies,
        'job_form': job_form,
    }
    return render(request, 'placements/manage_jobs.html', context)


@login_required
def post_job(request):
    if request.user.role != 'placement_officer':
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New job opening posted successfully.")
        else:
            messages.error(request, "Error posting job opening. Please check the inputs.")
            
    return redirect('manage_placements')


@login_required
def update_application_status(request, app_id, status):
    if request.user.role != 'placement_officer':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    application = get_object_or_404(JobApplication, id=app_id)
    
    if request.method == 'POST':
        comments = request.POST.get('placement_officer_comments', '')
        application.status = status
        application.placement_officer_comments = comments
        application.save()
        messages.success(request, f"Updated application status for {application.student.user.username} to {status.capitalize()}.")
        
    return redirect('manage_placements')
