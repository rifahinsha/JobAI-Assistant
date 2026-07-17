from functools import wraps
from django.shortcuts import redirect

from .models import Admin


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        admin_id = request.session.get('admin_id')
        if not admin_id or not Admin.objects.filter(pk=admin_id).exists():
            return redirect('admin_panel:admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper