from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import Profile


def get_profile(user):
    """Return the user's Profile, creating one if it is somehow missing."""
    default_role = Profile.Role.ADMIN if user.is_superuser else Profile.Role.MEMBER
    profile, _ = Profile.objects.get_or_create(user=user, defaults={'role': default_role})
    return profile


def role_required(role):
    """Allow only logged-in users whose profile has the given role.

    Logged-out users are sent to the login page (by @login_required).
    Logged-in users with a different role are sent back to their own
    dashboard with an error message.
    """

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if get_profile(request.user).role != role:
                messages.error(request, 'You do not have permission to open that page.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
