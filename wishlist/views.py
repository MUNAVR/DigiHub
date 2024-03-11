from django.shortcuts import render,redirect
from.models import *
from .models import Customers
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product_Variant
from app_1.decorators import check_blocked
from django.contrib import messages
# Create your views here.




@check_blocked
def add_to_wishlist(request, product_id):
    if 'email' not in request.session:
        return redirect('user:login')

    # Retrieve the user based on the email in the session
    email = request.session.get('email')
    user = get_object_or_404(Customers, email=email)

    # Retrieve the product variant based on the provided product_id
    product = get_object_or_404(Product_Variant, pk=product_id)
    
    # Retrieve or create the user's wishlist
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    
    # Add the product variant to the wishlist
    wishlist.products.add(product)

    # Add success message
    messages.success(request, f" added to your wishlist.")

    return redirect('user:index')


@check_blocked
def remove_from_wishlist(request, product_id):
    if 'email' not in request.session:
        return redirect('user:login')
    
    product = get_object_or_404(Product_Variant, pk=product_id)
    
    # Retrieve the user based on the email in the session
    email = request.session.get('email')
    user = get_object_or_404(Customers, email=email)
    
    wishlist = get_object_or_404(Wishlist, user=user)
    wishlist.remove_from_wishlist(product)

    # Add success message
    messages.success(request, f" removed from your wishlist.")
    
    return redirect('wishlist')

@check_blocked
def wishlist(request):
    if 'email' not in request.session:
        return redirect('user:login')
    
    # Retrieve the user based on the email in the session
    email = request.session.get('email')
    user = get_object_or_404(Customers, email=email)

    try:
        wishlist, created = Wishlist.objects.get_or_create(user=user)
    except Wishlist.DoesNotExist:
        messages.error(request, "Wishlist not found.")
        return redirect('user:index')

    return render(request, 'user_panel/wishlist.html', {'wishlist': wishlist})
