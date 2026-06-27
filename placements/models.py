from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class JobPosting(models.Model):
    JOB_TYPE_CHOICES = (
        ('full_time', 'Full-time'),
        ('internship', 'Internship'),
        ('contract', 'Contract'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=150)
    description = models.TextField()
    requirements = models.TextField(help_text="Skills, knowledge, and experience requirements")
    location = models.CharField(max_length=100, default='On-site')
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    salary_range = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. $80,000 - $100,000 or 12 LPA")
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00, help_text="Minimum CGPA required to apply")
    application_deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('interviewing', 'Interviewing'),
        ('offered', 'Offered'),
        ('rejected', 'Rejected'),
    )
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey('users.StudentProfile', on_delete=models.CASCADE, related_name='applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    resume_url = models.URLField(blank=True, null=True, help_text="Link to online resume or cloud document")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    placement_officer_comments = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('job_posting', 'student')

    def __str__(self):
        return f"{self.student.user.username} application for {self.job_posting.title}"
