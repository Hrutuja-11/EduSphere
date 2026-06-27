from django.core.exceptions import PermissionDenied
from functools import wraps

# -----------------------------------------------------------------------------
# ROLE-BASED ACCESS DECORATORS
# -----------------------------------------------------------------------------
# Purpose: These decorators act as security checkpoints. Before a view function 
# is allowed to run, the decorator checks if the logged-in user has the correct role.
# If they don't, it raises a PermissionDenied error (HTTP 403 Forbidden), 
# preventing unauthorized access.

def is_student(view_func):
    """
    Decorator for views that checks if the user is a Student.
    It uses @wraps to preserve the original view's metadata (like its name).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Ensure the user is logged in AND their role exactly matches 'student'
        if request.user.is_authenticated and request.user.role == 'student':
            return view_func(request, *args, **kwargs)
        # If not, strictly deny access.
        raise PermissionDenied("You must be a Student to view this page.")
    return _wrapped_view

def is_faculty(view_func):
    """Decorator to ensure only Faculty can access the view."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'faculty':
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("You must be Faculty to view this page.")
    return _wrapped_view

def is_hod(view_func):
    """Decorator to ensure only the HOD can access the view."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'hod':
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("You must be an HOD to view this page.")
    return _wrapped_view

def is_placement_officer(view_func):
    """Decorator to ensure only Placement Officers can access the view."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'placement_officer':
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("You must be a Placement Officer to view this page.")
    return _wrapped_view
