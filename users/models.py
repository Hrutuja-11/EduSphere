from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

# -----------------------------------------------------------------------------
# CORE USER MODEL
# -----------------------------------------------------------------------------
# Purpose: We use a CustomUser instead of Django's built-in User. 
# Implementation: Inheriting from AbstractUser gives us all standard auth features 
# (login, passwords) but allows us to add custom fields like 'role'.
class CustomUser(AbstractUser):
    # We define the available roles in the system using choices.
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('hod', 'HOD'),
        ('placement_officer', 'Placement Officer'),
    )
    
    # 'role' acts as the primary access control mechanism.
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    # Common fields applicable to everyone, regardless of their role.
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"


# -----------------------------------------------------------------------------
# ROLE-SPECIFIC PROFILE MODELS
# -----------------------------------------------------------------------------
# Purpose: A Student has very different data (enrollment number, major) than 
# a Faculty member (employee ID, department). Instead of cramming all possible 
# fields into CustomUser (which would result in many empty/null fields), we 
# create separate tables (Profiles) linked 1-to-1 with the CustomUser.

class StudentProfile(models.Model):
    # OneToOneField ensures that one CustomUser can only have ONE StudentProfile.
    # on_delete=models.CASCADE means if the User is deleted, delete this profile too.
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    
    # Student specific fields
    enrollment_number = models.CharField(max_length=50, blank=True, null=True)
    department = models.ForeignKey('academics.Department', on_delete=models.SET_NULL, blank=True, null=True, related_name='students')
    major = models.CharField(max_length=100, blank=True, null=True)
    current_semester = models.IntegerField(default=1)
    graduation_year = models.IntegerField(blank=True, null=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    skills = models.ManyToManyField('portfolio.Skill', blank=True, related_name='students')
    github = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    leetcode = models.URLField(blank=True, null=True)
    codeforces = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"Student Profile: {self.user.username}"


class FacultyProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='faculty_profile')
    
    # Faculty specific fields
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    department = models.ForeignKey('academics.Department', on_delete=models.SET_NULL, blank=True, null=True, related_name='faculty_members')
    designation = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Faculty Profile: {self.user.username}"


class HODProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='hod_profile')
    
    # HOD specific fields
    department = models.ForeignKey('academics.Department', on_delete=models.SET_NULL, blank=True, null=True, related_name='hods')
    department_managed = models.CharField(max_length=100, blank=True, null=True)
    office_location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"HOD Profile: {self.user.username}"


class PlacementOfficerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='placement_profile')
    
    # Placement Officer specific fields
    office_contact = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Placement Officer: {self.user.username}"


# -----------------------------------------------------------------------------
# SIGNALS (AUTO-CREATION OF PROFILES)
# -----------------------------------------------------------------------------
# Purpose: When a new CustomUser is created (e.g., via the Signup page), we 
# want to automatically create their corresponding empty Profile based on their role.
# Implementation: We use Django's 'post_save' signal, which fires immediately 
# after a model's .save() method finishes.

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    This function listens for the 'post_save' event from CustomUser.
    - 'instance' is the user object that was just saved.
    - 'created' is a boolean that is True ONLY when the user is created for the first time.
    """
    if created:
        # Check the role and create the appropriate profile table row.
        if instance.role == 'student':
            StudentProfile.objects.create(user=instance)
        elif instance.role == 'faculty':
            FacultyProfile.objects.create(user=instance)
        elif instance.role == 'hod':
            HODProfile.objects.create(user=instance)
            FacultyProfile.objects.create(user=instance)
        elif instance.role == 'placement_officer':
            PlacementOfficerProfile.objects.create(user=instance)

# This receiver ensures that when a User object is saved (updated), 
# the linked profile object is also saved, keeping them in sync.
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    # Try/except blocks handle cases where the profile might not exist yet
    try:
        if instance.role == 'student':
            instance.student_profile.save()
        elif instance.role == 'faculty':
            instance.faculty_profile.save()
        elif instance.role == 'hod':
            instance.hod_profile.save()
            if hasattr(instance, 'faculty_profile'):
                instance.faculty_profile.save()
        elif instance.role == 'placement_officer':
            instance.placement_profile.save()
    except Exception:
        # In a robust production app, you might want to log this error
        pass
