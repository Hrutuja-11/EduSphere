from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Avg
from users.models import StudentProfile
from .models import Course, CourseEnrollment, AttendanceRecord, ExamResult, TimetableEntry
from academics.forms import TimetableEntryForm, CourseForm
import datetime

@login_required
def academic_transcript(request, username):
    # Retrieve student profile
    student_profile = get_object_or_404(StudentProfile, user__username=username)
    
    # Access control: Student can only view their own transcript
    if request.user.role == 'student' and request.user.username != username:
        messages.error(request, "You do not have permission to view this transcript.")
        return redirect('dashboard')
        
    enrollments = student_profile.enrollments.all().select_related('course')
    avg_attendance = enrollments.aggregate(Avg('attendance_percentage'))['attendance_percentage__avg'] or 0.0
    
    context = {
        'student': student_profile,
        'enrollments': enrollments,
        'avg_attendance': round(avg_attendance, 1),
    }
    return render(request, 'academics/transcript.html', context)


@login_required
def mark_attendance(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Access control: Only HOD of the course's department or the assigned faculty can mark attendance
    if request.user.role == 'hod':
        if request.user.hod_profile.department != course.department:
            messages.error(request, "Access denied. This course belongs to another department.")
            return redirect('dashboard')
    elif request.user.role == 'faculty':
        if course.faculty != request.user.faculty_profile:
            messages.error(request, "Access denied. You are not assigned to teach this course.")
            return redirect('dashboard')
    else:
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    enrollments = CourseEnrollment.objects.filter(course=course).select_related('student__user')
    
    if request.method == 'POST':
        date_str = request.POST.get('date', str(datetime.date.today()))
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        present_student_ids = request.POST.getlist('present_students') # list of CourseEnrollment IDs
        
        # We process each enrollment in this course
        for enrollment in enrollments:
            is_present = str(enrollment.id) in present_student_ids
            status = 'present' if is_present else 'absent'
            
            # Save daily attendance record
            AttendanceRecord.objects.update_or_create(
                enrollment=enrollment,
                date=date,
                defaults={'status': status}
            )
            
            # Recalculate attendance percentage
            total_days = AttendanceRecord.objects.filter(enrollment=enrollment).count()
            present_days = AttendanceRecord.objects.filter(enrollment=enrollment, status='present').count()
            if total_days > 0:
                enrollment.attendance_percentage = (present_days / total_days) * 100.00
                enrollment.save()
                
        messages.success(request, f"Attendance marked for course {course.code} on {date}.")
        return redirect('dashboard')
        
    context = {
        'course': course,
        'enrollments': enrollments,
        'today': datetime.date.today().strftime("%Y-%m-%d"),
    }
    return render(request, 'academics/mark_attendance.html', context)


@login_required
def upload_grades(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Access control: Only HOD of the course's department or the assigned faculty can upload grades
    if request.user.role == 'hod':
        if request.user.hod_profile.department != course.department:
            messages.error(request, "Access denied. This course belongs to another department.")
            return redirect('dashboard')
    elif request.user.role == 'faculty':
        if course.faculty != request.user.faculty_profile:
            messages.error(request, "Access denied. You are not assigned to teach this course.")
            return redirect('dashboard')
    else:
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    enrollments = CourseEnrollment.objects.filter(course=course).select_related('student__user')
    
    if request.method == 'POST':
        for enrollment in enrollments:
            grade = request.POST.get(f'grade_{enrollment.id}', '').strip()
            if grade:
                enrollment.grade = grade
                enrollment.save()
                
        messages.success(request, f"Grades updated for course {course.code}.")
        return redirect('dashboard')
        
    context = {
        'course': course,
        'enrollments': enrollments,
    }
    return render(request, 'academics/upload_grades.html', context)


@login_required
def student_academics(request):
    if request.user.role != 'student':
        messages.error(request, "Only students can view this page.")
        return redirect('dashboard')
        
    profile = request.user.student_profile
    enrollments = profile.enrollments.all().select_related('course').prefetch_related('exam_results', 'attendance_records')
    
    grade_points_map = {
        'O': 10.0, 'A+': 10.0, 'A': 9.0, 'B+': 8.0, 'B': 7.0, 'C': 6.0, 'D': 5.0, 'F': 0.0,
        'o': 10.0, 'a+': 10.0, 'a': 9.0, 'b+': 8.0, 'b': 7.0, 'c': 6.0, 'd': 5.0, 'f': 0.0
    }
    
    # Group enrollments by semester
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
        
    sorted_semesters = sorted(semesters_dict.values(), key=lambda x: x['semester_num'])
    
    context = {
        'profile': profile,
        'semesters': sorted_semesters,
        'calculated_cgpa': calculated_cgpa,
        'total_credits_completed': total_credits,
    }
    return render(request, 'academics/student_academics.html', context)


@login_required
def add_timetable_entry(request):
    if request.user.role != 'hod':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    profile = request.user.hod_profile
    department = profile.department
    
    if request.method == 'POST':
        form = TimetableEntryForm(request.POST, department=department)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.department = department
            try:
                entry.save()
                messages.success(request, "Timetable entry added successfully.")
            except Exception:
                messages.error(request, "A schedule conflict exists for this day, slot, and semester.")
        else:
            messages.error(request, "Error adding timetable entry. Please check the values.")
            
    return redirect('dashboard')


@login_required
def delete_timetable_entry(request, entry_id):
    if request.user.role != 'hod':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    entry = get_object_or_404(TimetableEntry, id=entry_id, department=request.user.hod_profile.department)
    entry.delete()
    messages.success(request, "Timetable entry deleted successfully.")
    return redirect('dashboard')


@login_required
def add_course(request):
    if request.user.role != 'hod':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    profile = request.user.hod_profile
    department = profile.department
    
    if request.method == 'POST':
        form = CourseForm(request.POST, department=department)
        if form.is_valid():
            course = form.save(commit=False)
            course.department = department
            course.save()
            messages.success(request, f"Course '{course.name}' added successfully.")
        else:
            messages.error(request, "Error adding course. Please check the values.")
            
    return redirect('dashboard')


@login_required
def assign_faculty(request, course_id):
    if request.user.role != 'hod':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    profile = request.user.hod_profile
    department = profile.department
    
    course = get_object_or_404(Course, id=course_id, department=department)
    
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty_id')
        if faculty_id:
            from users.models import FacultyProfile
            faculty_profile = get_object_or_404(FacultyProfile, id=faculty_id, department=department)
            course.faculty = faculty_profile
            course.save()
            messages.success(request, f"Faculty '{faculty_profile.user.first_name or faculty_profile.user.username}' assigned to course '{course.name}'.")
        else:
            course.faculty = None
            course.save()
            messages.success(request, f"Faculty unassigned from course '{course.name}'.")
            
    return redirect('dashboard')
