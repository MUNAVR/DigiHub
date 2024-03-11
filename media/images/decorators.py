from functools import wraps
from django.contrib import messages
from app_1.models import Customers
from django.shortcuts import render,redirect


def check_blocked(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = Customers.objects.get(email=request.session.get('email'))
        if user.is_blocked:
            messages.error(request, "You are blocked. Please contact support for assistance.")
            return redirect('user:index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view