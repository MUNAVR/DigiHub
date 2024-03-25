from django.shortcuts import render, redirect, get_object_or_404
from coupon.models import *
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages

# Create your views here.
def admin_manage_coupons(request):
    if 'username' not in request.session:
        return redirect('admin_login') 
    
    coupons = Coupon.objects.all()
    return render(request, 'admin_panel/coupon_list.html', {'coupons': coupons})



def admin_create_coupon(request):
    if 'username' not in request.session:
        return redirect('admin_login') 
    
    if request.method == 'POST':
        code = request.POST.get('code')
        discount = request.POST.get('discount')
        validity_days = request.POST.get('validity_days')
        max_usage = request.POST.get('max_usage')
        active = request.POST.get('active')

        # Validation checks
        errors = {}

        # Check if coupon code is provided and meets criteria
        if not code or len(code) != 7 or not any(char.isdigit() for char in code) or not any(char.isalpha() for char in code):
            errors['code'] = "Coupon code must be exactly 7 characters long, containing at least one letter and one number."


        # Check if discount is within range
        try:
            discount = float(discount)
            if discount < 1 or discount > 100:
                errors['discount'] = "Discount must be between 1 and 100."
        except ValueError:
            errors['discount'] = "Discount must be a valid number."

        # Check if validity days is a positive integer
        try:
            validity_days = int(validity_days)
            if validity_days <= 0:
                errors['validity_days'] = "Validity days must be a positive integer."
        except ValueError:
            errors['validity_days'] = "Validity days must be a valid integer."

        # Check if max usage is a single digit between 1 and 10
        try:
            max_usage = int(max_usage)
            if max_usage < 1 or max_usage > 10:
                errors['max_usage'] = "Max usage must be a single digit between 1 and 10."
        except ValueError:
            errors['max_usage'] = "Max usage must be a valid integer."

        # If there are validation errors, return to form with errors
        if errors:
            return render(request, 'admin_panel/create_coupon.html', {'errors': errors})

        # If all validation checks pass, proceed with creating the coupon
        valid_from = timezone.now()
        valid_to = valid_from + timedelta(days=int(validity_days))

        coupon = Coupon.objects.create(
            code=code,
            discount=discount,
            valid_from=valid_from,
            valid_to=valid_to,
            max_usage=max_usage,
            active=active == 'on'  # Convert to boolean
        )
        return redirect('coupen_list')
    
    # If request method is not POST, render the form
    return render(request, 'admin_panel/create_coupon.html')


def change_active(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    # Toggle the active status of the coupon
    coupon.active = not coupon.active
    coupon.save()
    status = "activated" if coupon.active else "deactivated"
    messages.success(request, f"Coupon  {status} successfully.")
    return redirect('coupen_list') 