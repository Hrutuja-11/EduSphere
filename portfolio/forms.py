from django import forms
from .models import Project, Certification, Achievement, Endorsement

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'technologies_used', 'project_link', 'git_repository']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Portfolio Generator'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your project, goals, and outcomes...'}),
            'technologies_used': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python, Django, HTML, CSS'}),
            'project_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'e.g. https://myproject.com'}),
            'git_repository': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'e.g. https://github.com/user/project'}),
        }


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'issuing_organization', 'issue_date', 'expiry_date', 'credential_id', 'credential_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. AWS Certified Developer'}),
            'issuing_organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Amazon Web Services'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'credential_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Credential ID'}),
            'credential_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Verification URL'}),
        }


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'category', 'description', 'date', 'document_proof']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. First Place HackCSE'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your achievement details...'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'document_proof': forms.FileInput(attrs={'class': 'form-control'}),
        }


class EndorsementForm(forms.ModelForm):
    class Meta:
        model = Endorsement
        fields = ['relationship', 'content']
        widgets = {
            'relationship': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write endorsement here...'}),
        }
