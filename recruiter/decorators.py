from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def recruiter_required(view_func):
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.is_recruiter:
            messages.error(request, "That page is only available to recruiter accounts.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper