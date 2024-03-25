from django.shortcuts import render,get_object_or_404
from .models import *
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render,redirect
from products.models import Products, Product_Variant
from category.models import Brand
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from decimal import Decimal
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
# Create your views here.
from django.contrib.auth.decorators import login_required  # Import the login_required decorator
from django.utils.crypto import get_random_string

 # Add the login_required decorator to restrict access to authenticated users


def create_referral_offer(request):
    if 'username' not in request.session:
        return redirect('admin_login') 
    
    if request.method == 'POST':
        # Extract data from the request
        referral_amount = request.POST.get('amount')
        valid_from = timezone.now().date()
        valid_to = request.POST.get('valid_to')
        referred_by_id = request.POST.get('referred_by')

        # Check if all required fields are provided
        if not all([referral_amount, valid_to, referred_by_id]):
            error_message = "All fields are required."
            users = Customers.objects.all()
            context = {
                "user": users,
                "error_message": error_message
            }
            return render(request, 'admin_panel/create_offer.html', context)
        
        # Validate and convert valid_to to a date object
        try:
            valid_to = timezone.datetime.strptime(valid_to, '%Y-%m-%d').date()
        except ValueError:
            error_message = "Invalid date format for valid_to."
            users = Customers.objects.all()
            context = {
                "user": users,
                "error_message": error_message
            }
            return render(request, 'admin_panel/create_offer.html', context)
        
        # Validate referred_by_id
        try:
            referred_by_id = int(referred_by_id)
            referred_by = Customers.objects.get(id=referred_by_id)
        except (ValueError, Customers.DoesNotExist):
            error_message = "Invalid referred_by ID or user does not exist."
            users = Customers.objects.all()
            context = {
                "user": users,
                "error_message": error_message
            }
            return render(request, 'admin_panel/create_offer.html', context)
        
        # Generate unique offer and referral codes
        offer_code = get_random_string(length=10)
        referral_code = get_random_string(length=10)

       
        # Create the referral offer
        print(offer_code)
        print(referral_amount)
        print(valid_from)
        print(valid_to)
        print(referral_code)
        print(referred_by)
        obj = ReferralOffer.objects.create(
            offer_code=offer_code,
            referral_amount=referral_amount,
            valid_from=valid_from,
            valid_to=valid_to,
            referral_code=referral_code,
            referred_by=referred_by
        )
        obj.save()
        print(obj)
        
        # Add success message
        messages.success(request, 'Referral offer created successfully.')
        return redirect('referral_offer_list')
    
    # Fetch users for referral selection
    users = Customers.objects.all()
    context = {
        "user": users
    }
    return render(request, 'admin_panel/create_offer.html', context)



def display_referral_offers(request):
    if 'username' not in request.session:
        return redirect('admin_login') 
    
    offers = ReferralOffer.objects.all()
    print(offers)
    context={
        "referral_offers":offers
    }
    return render(request, 'admin_panel/referral_offer_list.html',context)

def referral_active(request, offer_id):
    offer = get_object_or_404(ReferralOffer, id=offer_id)
    # Toggle the active status of the coupon
    offer.is_active = not offer.is_active
    offer.save()

    # Add success message
    status = "activated" if offer.is_active else "deactivated"
    messages.success(request, f"Referral offer {status} successfully.")

    return redirect('referral_offer_list')