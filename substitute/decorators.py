from django.http import HttpResponse
from django.shortcuts import redirect

# Restricting access to pages based on user type


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        # Checking authentication
        if request.user.is_authenticated:
            # Checking user role
            if request.user.is_admin:
                return redirect('admin:index')
            else:
                return redirect("teacher_home")
        else:
            return view_func(request, *args, **kwargs)
        return view_func(request, *args, **kwargs)
    return wrapper_func
