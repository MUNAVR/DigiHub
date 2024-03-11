from functools import wraps
from django.contrib import messages
from app_1.models import Customers
from django.shortcuts import render,redirect


from django.core.exceptions import ObjectDoesNotExist

def check_blocked(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        email = request.session.get('email')
        if email:
            try:
                user = Customers.objects.get(email=email)
                if user.is_blocked:
                    messages.error(request, "You are blocked. Please contact support for assistance.")
                    return redirect('user:index')
            except ObjectDoesNotExist:
                messages.error(request, "User not found. Please log in again.")
                return redirect('user:login')
        else:
            messages.error(request, "You are not logged in.")
            return redirect('user:login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view
