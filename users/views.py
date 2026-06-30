from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome {user.username}.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

# -----------------------------------------------------------------------------
# UNIFIED DASHBOARD ROUTING
# -----------------------------------------------------------------------------
# Purpose: Instead of having 4 different URLs (e.g., /student-dashboard, /faculty-dashboard),
# we use a single clean URL: /dashboard/.
# Implementation: This view checks the logged-in user's role and renders the 
# HTML template specifically designed for that role. This keeps URLs clean and 
# centralizes the routing logic.

from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from users.models import StudentProfile, FacultyProfile, HODProfile, PlacementOfficerProfile
from users.forms import UserProfileForm, StudentProfileForm, FacultyProfileForm, HODProfileForm, PlacementOfficerProfileForm

@login_required
def dashboard_view(request):
    role = request.user.role
    
    if role == 'student':
        profile = request.user.student_profile
        enrollments = profile.enrollments.all().select_related('course').prefetch_related('exam_results', 'attendance_records')
        
        # Grade to grade-points mapping
        grade_points_map = {
            'O': 10.0, 'A+': 10.0, 'A': 9.0, 'B+': 8.0, 'B': 7.0, 'C': 6.0, 'D': 5.0, 'F': 0.0,
            'o': 10.0, 'a+': 10.0, 'a': 9.0, 'b+': 8.0, 'b': 7.0, 'c': 6.0, 'd': 5.0, 'f': 0.0
        }
        
        # Group enrollments by semester and calculate stats
        semesters_dict = {}
        total_points = 0.0
        total_credits = 0
        
        for enroll in enrollments:
            # Precalculate attendance counts
            enroll.total_days = enroll.attendance_records.count()
            enroll.present_count = enroll.attendance_records.filter(status='present').count()
            enroll.absent_count = enroll.attendance_records.filter(status='absent').count()
            
            sem = enroll.semester
            if sem not in semesters_dict:
                semesters_dict[sem] = {
                    'semester_num': sem,
                    'enrollments': [],
                    'total_points': 0.0,
                    'total_credits': 0,
                    'sgpa': 0.0
                }
            semesters_dict[sem]['enrollments'].append(enroll)
            
            grade = enroll.grade
            if grade and grade.upper() in grade_points_map:
                pts = grade_points_map[grade.upper()]
                credits = enroll.course.credits
                semesters_dict[sem]['total_points'] += float(pts * credits)
                semesters_dict[sem]['total_credits'] += credits
                
                total_points += float(pts * credits)
                total_credits += credits

        for sem, data in semesters_dict.items():
            if data['total_credits'] > 0:
                data['sgpa'] = round(data['total_points'] / data['total_credits'], 2)
            else:
                data['sgpa'] = 0.0
                
        calculated_cgpa = 0.0
        if total_credits > 0:
            calculated_cgpa = round(total_points / total_credits, 2)
            
        # Update/sync CGPA on the profile model if it has changed
        if float(profile.cgpa) != float(calculated_cgpa):
            profile.cgpa = calculated_cgpa
            profile.save(update_fields=['cgpa'])
            
        sorted_semesters = sorted(semesters_dict.values(), key=lambda x: x['semester_num'])
        
        # Calculate dynamic average attendance
        avg_att = enrollments.aggregate(Avg('attendance_percentage'))['attendance_percentage__avg'] or 0.0
        
        # Calculate portfolio completion
        completion = 0
        if profile.enrollment_number: completion += 15
        if profile.department: completion += 15
        if profile.graduation_year: completion += 15
        if profile.skills.exists(): completion += 15
        if profile.projects.exists(): completion += 20
        if profile.certifications.exists(): completion += 20
        
        projects = profile.projects.all()
        certifications = profile.certifications.all()
        achievements = profile.achievements.all()
        endorsements = profile.endorsements.all().select_related('faculty__user')
        applications = profile.applications.all().select_related('job_posting__company')
        
        # Filter enrollments for the current semester in Python to reuse prefetched data
        current_enrollments = [e for e in enrollments if e.semester == profile.current_semester]
        
        # Load actual database timetable entries
        from academics.models import TimetableEntry
        
        db_entries = TimetableEntry.objects.filter(
            department=profile.department, 
            semester=profile.current_semester
        ).select_related('course')
        
        timetable_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        timetable_slots = [
            '09:00 AM - 10:30 AM',
            '10:45 AM - 12:15 PM',
            '01:30 PM - 03:00 PM',
            '03:15 PM - 04:45 PM'
        ]
        
        timetable_list = []
        for day in timetable_days:
            day_slots = []
            for slot in timetable_slots:
                entry = next((e for e in db_entries if e.day == day and e.slot == slot), None)
                slot_course = None
                if entry:
                    slot_course = {
                        'code': entry.course.code,
                        'name': entry.course.name,
                        'credits': entry.course.credits
                    }
                day_slots.append({
                    'time': slot,
                    'course': slot_course
                })
            timetable_list.append({
                'day': day,
                'slots': day_slots
            })
        
        # Get student daily activities
        activities = profile.activities.all().select_related('logged_by__user').order_by('-date')
        
        context = {
            'profile': profile,
            'enrollments': current_enrollments,
            'calculated_cgpa': calculated_cgpa,
            'avg_attendance': round(avg_att, 1),
            'portfolio_completion': completion,
            'projects': projects,
            'certifications': certifications,
            'achievements': achievements,
            'endorsements': endorsements,
            'applications': applications,
            'timetable': timetable_list,
            'timetable_slots': timetable_slots,
            'has_timetable': db_entries.exists(),
            'activities': activities,
        }
        return render(request, 'dashboards/student.html', context)
        
    elif role == 'faculty':
        profile = request.user.faculty_profile
        dept = profile.department
        
        from portfolio.models import Project, Certification, Achievement
        from academics.models import Course
        
        # Filter items where student is in the same department
        pending_projects = Project.objects.filter(student__department=dept, verification_status='pending').select_related('student__user')
        pending_certs = Certification.objects.filter(student__department=dept, verification_status='pending').select_related('student__user')
        pending_achievements = Achievement.objects.filter(student__department=dept, verification_status='pending').select_related('student__user')
        
        dept_students = StudentProfile.objects.filter(department=dept).select_related('user')
        courses = Course.objects.filter(department=dept)
        
        from academics.models import ClassIncharge
        incharge_classes = ClassIncharge.objects.filter(faculty=profile).select_related('department')
        incharge_students = StudentProfile.objects.filter(
            department=dept,
            current_semester__in=[c.semester for c in incharge_classes]
        ).select_related('user')
        
        context = {
            'profile': profile,
            'department': dept,
            'pending_projects': pending_projects,
            'pending_certs': pending_certs,
            'pending_achievements': pending_achievements,
            'students': dept_students,
            'courses': courses,
            'incharge_classes': incharge_classes,
            'incharge_students': incharge_students,
        }
        return render(request, 'dashboards/faculty.html', context)
        
    elif role == 'hod':
        profile = request.user.hod_profile
        dept = profile.department
        
        students = StudentProfile.objects.filter(department=dept).select_related('user')
        faculty_members = FacultyProfile.objects.filter(department=dept).select_related('user')
        
        avg_gpa = students.aggregate(Avg('cgpa'))['cgpa__avg'] or 0.0
        
        from academics.models import CourseEnrollment
        avg_att = CourseEnrollment.objects.filter(student__department=dept).aggregate(Avg('attendance_percentage'))['attendance_percentage__avg'] or 0.0
        
        # Placement count in department
        placed_count = students.filter(applications__status='offered').distinct().count()
        total_students = students.count()
        placement_rate = (placed_count / total_students * 100) if total_students > 0 else 0.0
        
        # Load HOD department course and timetable management entries
        from academics.models import TimetableEntry, Course
        from academics.forms import TimetableEntryForm, CourseForm
        
        courses = Course.objects.filter(department=dept).select_related('faculty__user').order_by('semester', 'code')
        timetable_entries = TimetableEntry.objects.filter(department=dept).select_related('course').order_by('semester', 'day', 'slot')
        timetable_form = TimetableEntryForm(department=dept)
        course_form = CourseForm(department=dept)
        
        from academics.models import ClassIncharge
        class_incharges = ClassIncharge.objects.filter(department=dept).select_related('faculty__user')
        incharges_dict = {ci.semester: ci for ci in class_incharges}
        semesters_incharges = []
        for sem in range(1, 9):
            semesters_incharges.append({
                'semester': sem,
                'incharge': incharges_dict.get(sem)
            })
        
        context = {
            'profile': profile,
            'department': dept,
            'students': students,
            'faculty_members': faculty_members,
            'avg_cgpa': round(avg_gpa, 2),
            'avg_attendance': round(avg_att, 1),
            'placed_count': placed_count,
            'total_students': total_students,
            'placement_rate': round(placement_rate, 1),
            'courses': courses,
            'course_form': course_form,
            'timetable_entries': timetable_entries,
            'timetable_form': timetable_form,
            'class_incharges': class_incharges,
            'semesters_incharges': semesters_incharges,
        }
        return render(request, 'dashboards/hod.html', context)

        
    elif role == 'placement_officer':
        from placements.models import JobPosting, JobApplication
        from portfolio.models import Skill
        
        profile = request.user.placement_profile
        active_postings = JobPosting.objects.filter(is_active=True).select_related('company')
        applications = JobApplication.objects.all().select_related('student__user', 'job_posting__company')
        students = StudentProfile.objects.all().select_related('user', 'department')
        skills = Skill.objects.all()
        
        context = {
            'profile': profile,
            'active_postings': active_postings,
            'applications': applications,
            'students': students,
            'skills': skills,
        }
        return render(request, 'dashboards/placement.html', context)
        
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    role = user.role
    
    if role == 'student':
        profile = user.student_profile
        profile_form_class = StudentProfileForm
    elif role == 'faculty':
        profile = user.faculty_profile
        profile_form_class = FacultyProfileForm
    elif role == 'hod':
        profile = user.hod_profile
        profile_form_class = HODProfileForm
    elif role == 'placement_officer':
        profile = user.placement_profile
        profile_form_class = PlacementOfficerProfileForm
    else:
        profile = None
        profile_form_class = None
        
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        if profile_form_class:
            profile_form = profile_form_class(request.POST, instance=profile)
        else:
            profile_form = None
            
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserProfileForm(instance=user)
        if profile_form_class:
            profile_form = profile_form_class(instance=profile)
        else:
            profile_form = None
            
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'role': role,
    }
    return render(request, 'users/profile.html', context)
