from django.shortcuts import render, redirect
from .models import *
from app_1.models import Customers
from products.models import Product_Variant
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


# Create your views here.

def shop_cart(request):
    if 'email' not in request.session:
        return redirect('user:login')  # Redirect to login page if not logged in

    # Retrieve user information from session
    email = request.session['email']

    # Get user object based on email
    user = Customers.objects.get(email=email)

    cart_items = Cart.objects.filter(user_id=user)

    context = {
        'cart_items': cart_items,
    }

    return render(request, "user_panel/shop_cart.html", context)



def add_cart(request, variant_id):
    # Check if 'email' key exists in the session
    if 'email' not in request.session:
        return redirect('user:login')  # Redirect to login page if not logged in

    # Retrieve user information from session
    email = request.session['email']

    # Get user object based on email
    user = Customers.objects.get(email=email)

    # Get product variant object based on variant_id
    product = Product_Variant.objects.get(pk=variant_id)

    # Create or get cart item for the user and product
    cart_item, created = Cart.objects.get_or_create(user_id=user, product_variant=product)

    # If cart item already exists, increment its quantity
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Redirect to the cart page after adding the item
    return redirect('user:index')
# Assuming 'cart' is the name of your cart page


def delete_cart_item(request, cart_item_id):
    # Retrieve the cart item to delete
    try:
        cart_item = Cart.objects.get(pk=cart_item_id)
    except Cart.DoesNotExist:
        # Handle the case where the cart item does not exist
        # You might redirect the user to the cart page or display an error message
        return redirect('shop_cart')

    # Delete the cart item
    cart_item.delete()

    # Redirect the user back to the cart page after deletion
    return redirect('shop_cart')

# views.py


def update_cart_item(request):
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')
        action = request.POST.get('action')

        cart_item = Cart.objects.get(pk=cart_item_id)

        if action == 'increase':
            if cart_item.product_variant.stock > cart_item.quantity:
                cart_item.quantity += 1
                cart_item.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Not enough stock'})
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                return JsonResponse({'success': True})
            else:
                # Optionally, you can delete the item from the cart if quantity becomes zero
                # cart_item.delete()
                return JsonResponse({'success': False, 'error': 'Quantity cannot be less than 1'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})





