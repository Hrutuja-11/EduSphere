from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Avg
from users.models import StudentProfile
from .models import Course, CourseEnrollment, AttendanceRecord, ExamResult, TimetableEntry, ClassIncharge, StudentActivity
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
    
    can_access = False
    if request.user.role == 'hod':
        if request.user.hod_profile.department == course.department:
            can_access = True
    elif request.user.role == 'faculty':
        if course.faculty == request.user.faculty_profile:
            can_access = True
        else:
            can_access = ClassIncharge.objects.filter(
                faculty=request.user.faculty_profile,
                department=course.department,
                semester=course.semester
            ).exists()
            
    if not can_access:
        messages.error(request, "Access denied. You are not authorized to mark attendance for this course.")
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
    
    can_access = False
    if request.user.role == 'hod':
        if request.user.hod_profile.department == course.department:
            can_access = True
    elif request.user.role == 'faculty':
        if course.faculty == request.user.faculty_profile:
            can_access = True
        else:
            can_access = ClassIncharge.objects.filter(
                faculty=request.user.faculty_profile,
                department=course.department,
                semester=course.semester
            ).exists()
            
    if not can_access:
        messages.error(request, "Access denied. You are not authorized to upload grades for this course.")
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


@login_required
def assign_class_incharge(request):
    if request.user.role != 'hod':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    profile = request.user.hod_profile
    department = profile.department
    
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty_id')
        semester = request.POST.get('semester')
        
        if not semester:
            messages.error(request, "Semester is required.")
            return redirect('dashboard')
            
        try:
            semester = int(semester)
        except ValueError:
            messages.error(request, "Invalid semester value.")
            return redirect('dashboard')
            
        if faculty_id:
            from users.models import FacultyProfile
            faculty_profile = get_object_or_404(FacultyProfile, id=faculty_id, department=department)
            # Update or create the ClassIncharge assignment
            ClassIncharge.objects.update_or_create(
                department=department,
                semester=semester,
                defaults={'faculty': faculty_profile}
            )
            messages.success(request, f"Faculty '{faculty_profile.user.first_name or faculty_profile.user.username}' assigned as Class Incharge for Semester {semester}.")
        else:
            # Remove ClassIncharge for that semester
            ClassIncharge.objects.filter(department=department, semester=semester).delete()
            messages.success(request, f"Class Incharge removed for Semester {semester}.")
            
    return redirect('dashboard')


@login_required
def manage_student_class(request, student_id):
    from users.models import StudentProfile
    from academics.models import ClassIncharge, StudentActivity, CourseEnrollment, ExamResult
    
    student = get_object_or_404(StudentProfile, id=student_id)
    user = request.user
    
    # Access Control: Only HOD of the student's department OR assigned Class Incharge of student's current semester/dept
    can_manage = False
    if user.role == 'hod' and user.hod_profile.department == student.department:
        can_manage = True
    elif user.role == 'faculty':
        is_incharge = ClassIncharge.objects.filter(
            faculty=user.faculty_profile,
            department=student.department,
            semester=student.current_semester
        ).exists()
        if is_incharge:
            can_manage = True
            
    if not can_manage:
        messages.error(request, "Access denied. You are not authorized to manage this student.")
        return redirect('dashboard')
        
    enrollments = CourseEnrollment.objects.filter(student=student, semester=student.current_semester).select_related('course')
    exam_results = ExamResult.objects.filter(enrollment__in=enrollments).select_related('enrollment__course')
    activities = StudentActivity.objects.filter(student=student).select_related('logged_by__user').order_by('-date')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_academics':
            # Update student overall semester promotion
            new_semester = request.POST.get('current_semester')
            if new_semester:
                try:
                    student.current_semester = int(new_semester)
                    student.save()
                except ValueError:
                    pass
            
            # Update each course enrollment grades and attendance
            for enroll in enrollments:
                att_val = request.POST.get(f'attendance_{enroll.id}')
                grade_val = request.POST.get(f'grade_{enroll.id}')
                if att_val is not None:
                    try:
                        enroll.attendance_percentage = float(att_val)
                    except ValueError:
                        pass
                if grade_val is not None:
                    enroll.grade = grade_val.strip()
                enroll.save()
            messages.success(request, f"Academic details updated for {student.user.first_name or student.user.username}.")
            return redirect('manage_student_class', student_id=student.id)
            
        elif action == 'add_marks':
            enrollment_id = request.POST.get('enrollment_id')
            assessment_name = request.POST.get('assessment_name')
            max_marks = request.POST.get('max_marks')
            marks_obtained = request.POST.get('marks_obtained')
            
            if enrollment_id and assessment_name and max_marks and marks_obtained:
                enroll = get_object_or_404(CourseEnrollment, id=enrollment_id, student=student)
                try:
                    ExamResult.objects.create(
                        enrollment=enroll,
                        assessment_name=assessment_name.strip(),
                        max_marks=float(max_marks),
                        marks_obtained=float(marks_obtained)
                    )
                    messages.success(request, f"Marks added for {enroll.course.code}.")
                except ValueError:
                    messages.error(request, "Invalid marks values.")
            else:
                messages.error(request, "Please fill out all fields to add marks.")
            return redirect('manage_student_class', student_id=student.id)
            
        elif action == 'delete_marks':
            result_id = request.POST.get('result_id')
            if result_id:
                result = get_object_or_404(ExamResult, id=result_id, enrollment__student=student)
                result.delete()
                messages.success(request, "Exam result entry deleted.")
            return redirect('manage_student_class', student_id=student.id)
            
        elif action == 'add_activity':
            activity_type = request.POST.get('activity_type')
            description = request.POST.get('description')
            date_str = request.POST.get('date', str(datetime.date.today()))
            
            if activity_type and description:
                try:
                    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    date = datetime.date.today()
                
                logged_by = user.faculty_profile if user.role == 'faculty' else None
                StudentActivity.objects.create(
                    student=student,
                    date=date,
                    activity_type=activity_type.strip(),
                    description=description.strip(),
                    logged_by=logged_by
                )
                messages.success(request, "Daily activity logged successfully.")
            else:
                messages.error(request, "Please fill out all activity fields.")
            return redirect('manage_student_class', student_id=student.id)
            
        elif action == 'delete_activity':
            activity_id = request.POST.get('activity_id')
            if activity_id:
                act = get_object_or_404(StudentActivity, id=activity_id, student=student)
                act.delete()
                messages.success(request, "Daily activity entry deleted.")
            return redirect('manage_student_class', student_id=student.id)
            
    context = {
        'student': student,
        'enrollments': enrollments,
        'exam_results': exam_results,
        'activities': activities,
        'today': datetime.date.today().strftime("%Y-%m-%d"),
    }
    return render(request, 'academics/manage_student.html', context)
