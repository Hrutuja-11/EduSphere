from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    VERIFICATION_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )
    student = models.ForeignKey('users.StudentProfile', on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=150)
    description = models.TextField()
    technologies_used = models.CharField(max_length=200, help_text="Comma-separated list of technologies (e.g. Django, React, Postgres)")
    project_link = models.URLField(blank=True, null=True)
    git_repository = models.URLField(blank=True, null=True)
    
    verification_status = models.CharField(max_length=15, choices=VERIFICATION_CHOICES, default='pending')
    verified_by = models.ForeignKey('users.FacultyProfile', on_delete=models.SET_NULL, blank=True, null=True, related_name='verified_projects')
    verification_date = models.DateTimeField(blank=True, null=True)
    faculty_comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.student.user.username}"


class Certification(models.Model):
    VERIFICATION_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )
    student = models.ForeignKey('users.StudentProfile', on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=150)
    issuing_organization = models.CharField(max_length=100)
    issue_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    credential_id = models.CharField(max_length=100, blank=True, null=True)
    credential_url = models.URLField(blank=True, null=True)
    
    verification_status = models.CharField(max_length=15, choices=VERIFICATION_CHOICES, default='pending')
    verified_by = models.ForeignKey('users.FacultyProfile', on_delete=models.SET_NULL, blank=True, null=True, related_name='verified_certifications')
    verification_date = models.DateTimeField(blank=True, null=True)
    faculty_comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.student.user.username}"


class Achievement(models.Model):
    VERIFICATION_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )
    CATEGORY_CHOICES = (
        ('academic', 'Academic'),
        ('extracurricular', 'Extracurricular'),
        ('sports', 'Sports'),
        ('research', 'Research'),
        ('other', 'Other'),
    )
    student = models.ForeignKey('users.StudentProfile', on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='extracurricular')
    description = models.TextField()
    date = models.DateField()
    document_proof = models.FileField(upload_to='achievements/', blank=True, null=True)
    
    verification_status = models.CharField(max_length=15, choices=VERIFICATION_CHOICES, default='pending')
    verified_by = models.ForeignKey('users.FacultyProfile', on_delete=models.SET_NULL, blank=True, null=True, related_name='verified_achievements')
    verification_date = models.DateTimeField(blank=True, null=True)
    faculty_comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()}) - {self.student.user.username}"


class Endorsement(models.Model):
    RELATIONSHIP_CHOICES = (
        ('class_teacher', 'Class Teacher'),
        ('project_guide', 'Project Guide'),
        ('mentor', 'Mentor'),
        ('other', 'Other'),
    )
    student = models.ForeignKey('users.StudentProfile', on_delete=models.CASCADE, related_name='endorsements')
    faculty = models.ForeignKey('users.FacultyProfile', on_delete=models.CASCADE, related_name='given_endorsements')
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, default='mentor')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Endorsement for {self.student.user.username} by {self.faculty.user.username}"
