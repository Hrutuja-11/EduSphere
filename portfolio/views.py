from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from users.models import StudentProfile, FacultyProfile
from .models import Skill, Project, Certification, Achievement, Endorsement
from .forms import ProjectForm, CertificationForm, AchievementForm, EndorsementForm

def public_portfolio(request, username):
    student = get_object_or_404(StudentProfile, user__username=username)
    
    # Public portfolio strictly shows verified items to maintain credibility for recruiters
    projects = student.projects.filter(verification_status='verified')
    certifications = student.certifications.filter(verification_status='verified')
    achievements = student.achievements.filter(verification_status='verified')
        
    endorsements = student.endorsements.all().select_related('faculty__user')
    
    context = {
        'student': student,
        'projects': projects,
        'certifications': certifications,
        'achievements': achievements,
        'endorsements': endorsements,
    }
    return render(request, 'portfolio/public_portfolio.html', context)


@login_required
def manage_portfolio(request):
    if request.user.role != 'student':
        messages.error(request, "Only students can manage their portfolios.")
        return redirect('dashboard')
        
    student = request.user.student_profile
    projects = student.projects.all()
    certifications = student.certifications.all()
    achievements = student.achievements.all()
    all_skills = Skill.objects.all()
    student_skills = student.skills.all()
    
    project_form = ProjectForm()
    cert_form = CertificationForm()
    ach_form = AchievementForm()
    
    context = {
        'student': student,
        'projects': projects,
        'certifications': certifications,
        'achievements': achievements,
        'all_skills': all_skills,
        'student_skills': student_skills,
        'project_form': project_form,
        'cert_form': cert_form,
        'ach_form': ach_form,
    }
    return render(request, 'portfolio/manage_portfolio.html', context)


@login_required
def add_project(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.student = request.user.student_profile
            project.verification_status = 'pending'
            project.save()
            messages.success(request, "Project added successfully and sent for faculty verification.")
        else:
            messages.error(request, "Error adding project. Please verify inputs.")
    return redirect('manage_portfolio')


@login_required
def edit_project(request, project_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    project = get_object_or_404(Project, id=project_id, student=request.user.student_profile)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project.verification_status = 'pending' # Reset status on edit
            project.save()
            messages.success(request, "Project updated successfully and sent for re-verification.")
        else:
            messages.error(request, "Error updating project.")
    return redirect('manage_portfolio')


@login_required
def delete_project(request, project_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    project = get_object_or_404(Project, id=project_id, student=request.user.student_profile)
    project.delete()
    messages.success(request, "Project removed from portfolio.")
    return redirect('manage_portfolio')


@login_required
def add_certification(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    if request.method == 'POST':
        form = CertificationForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.student = request.user.student_profile
            cert.verification_status = 'pending'
            cert.save()
            messages.success(request, "Certification added successfully and sent for faculty verification.")
        else:
            messages.error(request, "Error adding certification.")
    return redirect('manage_portfolio')


@login_required
def edit_certification(request, cert_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    cert = get_object_or_404(Certification, id=cert_id, student=request.user.student_profile)
    if request.method == 'POST':
        form = CertificationForm(request.POST, instance=cert)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.verification_status = 'pending'
            cert.save()
            messages.success(request, "Certification updated successfully and sent for re-verification.")
        else:
            messages.error(request, "Error updating certification.")
    return redirect('manage_portfolio')


@login_required
def delete_certification(request, cert_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    cert = get_object_or_404(Certification, id=cert_id, student=request.user.student_profile)
    cert.delete()
    messages.success(request, "Certification removed.")
    return redirect('manage_portfolio')


@login_required
def add_achievement(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    if request.method == 'POST':
        form = AchievementForm(request.POST, request.FILES)
        if form.is_valid():
            ach = form.save(commit=False)
            ach.student = request.user.student_profile
            ach.verification_status = 'pending'
            ach.save()
            messages.success(request, "Achievement added successfully and sent for faculty verification.")
        else:
            messages.error(request, "Error adding achievement.")
    return redirect('manage_portfolio')


@login_required
def edit_achievement(request, ach_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    ach = get_object_or_404(Achievement, id=ach_id, student=request.user.student_profile)
    if request.method == 'POST':
        form = AchievementForm(request.POST, request.FILES, instance=ach)
        if form.is_valid():
            ach = form.save(commit=False)
            ach.verification_status = 'pending'
            ach.save()
            messages.success(request, "Achievement updated successfully and sent for re-verification.")
        else:
            messages.error(request, "Error updating achievement.")
    return redirect('manage_portfolio')


@login_required
def delete_achievement(request, ach_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    ach = get_object_or_404(Achievement, id=ach_id, student=request.user.student_profile)
    ach.delete()
    messages.success(request, "Achievement removed.")
    return redirect('manage_portfolio')


@login_required
def update_skills(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    if request.method == 'POST':
        selected_skill_ids = request.POST.getlist('skills')
        student = request.user.student_profile
        student.skills.set(selected_skill_ids)
        messages.success(request, "Skills updated successfully.")
    return redirect('manage_portfolio')


@login_required
def verify_item(request, item_type, item_id, action):
    if request.user.role not in ['faculty', 'hod']:
        messages.error(request, "Only faculty members can verify achievements.")
        return redirect('dashboard')
        
    faculty = request.user.faculty_profile
    
    if item_type == 'project':
        item = get_object_or_404(Project, id=item_id)
    elif item_type == 'certification':
        item = get_object_or_404(Certification, id=item_id)
    elif item_type == 'achievement':
        item = get_object_or_404(Achievement, id=item_id)
    else:
        messages.error(request, "Invalid item type.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        comments = request.POST.get('faculty_comments', '')
        item.faculty_comments = comments
        item.verified_by = faculty
        item.verification_date = timezone.now()
        
        if action == 'approve':
            item.verification_status = 'verified'
            messages.success(request, f"Successfully verified {item.student.user.username}'s {item_type}.")
        elif action == 'reject':
            item.verification_status = 'rejected'
            messages.error(request, f"Rejected {item.student.user.username}'s {item_type}.")
            
        item.save()
        
    return redirect('dashboard')


@login_required
def add_endorsement(request, student_id):
    if request.user.role not in ['faculty', 'hod']:
        messages.error(request, "Only faculty members can endorse students.")
        return redirect('dashboard')
        
    student = get_object_or_404(StudentProfile, id=student_id)
    faculty = request.user.faculty_profile
    
    if request.method == 'POST':
        form = EndorsementForm(request.POST)
        if form.is_valid():
            endorsement = form.save(commit=False)
            endorsement.student = student
            endorsement.faculty = faculty
            endorsement.save()
            messages.success(request, f"Endorsement submitted for {student.user.username}.")
        else:
            messages.error(request, "Error submitting endorsement.")
            
    return redirect('dashboard')


@login_required
def update_contact_info(request):
    if request.user.role != 'student':
        messages.error(request, "Only students can update their contact info.")
        return redirect('dashboard')
        
    profile = request.user.student_profile
    user = request.user
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone_number
        user.save()
        
        profile.github = request.POST.get('github', '').strip()
        profile.linkedin = request.POST.get('linkedin', '').strip()
        profile.leetcode = request.POST.get('leetcode', '').strip()
        profile.codeforces = request.POST.get('codeforces', '').strip()
        profile.location = request.POST.get('location', '').strip()
        profile.save()
        
        messages.success(request, "Contact information updated successfully.")
        
    return redirect('manage_portfolio')
