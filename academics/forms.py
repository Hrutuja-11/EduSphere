from django import forms
from .models import TimetableEntry, Course
from users.models import FacultyProfile

class TimetableEntryForm(forms.ModelForm):
    class Meta:
        model = TimetableEntry
        fields = ('course', 'day', 'slot', 'semester')

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        super().__init__(*args, **kwargs)
        if department:
            self.fields['course'].queryset = Course.objects.filter(department=department)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('name', 'code', 'credits', 'semester', 'faculty')

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        super().__init__(*args, **kwargs)
        if department:
            self.fields['faculty'].queryset = FacultyProfile.objects.filter(department=department)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

