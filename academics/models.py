from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    credits = models.IntegerField(default=3)
    semester = models.IntegerField(default=1)
    faculty = models.ForeignKey('users.FacultyProfile', on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_courses')

    def __str__(self):
        return f"{self.code} - {self.name}"


class CourseEnrollment(models.Model):
    student = models.ForeignKey('users.StudentProfile', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    semester = models.IntegerField()
    grade = models.CharField(max_length=5, blank=True, null=True)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)

    class Meta:
        unique_together = ('student', 'course', 'semester')

    def __str__(self):
        return f"{self.student.user.username} enrolled in {self.course.code}"


class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )
    enrollment = models.ForeignKey(CourseEnrollment, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('enrollment', 'date')

    def __str__(self):
        return f"{self.enrollment.student.user.username} - {self.enrollment.course.code} - {self.date}: {self.status}"


class ExamResult(models.Model):
    enrollment = models.ForeignKey(CourseEnrollment, on_delete=models.CASCADE, related_name='exam_results')
    assessment_name = models.CharField(max_length=50) # e.g. "Quiz 1", "Midterm", "End Semester"
    max_marks = models.DecimalField(max_digits=5, decimal_places=2)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.enrollment.student.user.username} - {self.enrollment.course.code} - {self.assessment_name}: {self.marks_obtained}/{self.max_marks}"


class TimetableEntry(models.Model):
    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    )
    SLOT_CHOICES = (
        ('09:00 AM - 10:30 AM', '09:00 AM - 10:30 AM'),
        ('10:45 AM - 12:15 PM', '10:45 AM - 12:15 PM'),
        ('01:30 PM - 03:00 PM', '01:30 PM - 03:00 PM'),
        ('03:15 PM - 04:45 PM', '03:15 PM - 04:45 PM'),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='timetable_entries')
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    slot = models.CharField(max_length=50, choices=SLOT_CHOICES)
    semester = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='timetable_entries')

    class Meta:
        unique_together = ('day', 'slot', 'semester', 'department')

    def __str__(self):
        return f"{self.course.code} - {self.day} {self.slot} (Sem {self.semester})"
