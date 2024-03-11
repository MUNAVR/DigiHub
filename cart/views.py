from django.shortcuts import render, redirect
from .models import *
from app_1.models import Customers
from products.models import Product_Variant
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from app_1.decorators import check_blocked
from django.shortcuts import redirect, get_object_or_404

from wishlist.models import Wishlist


# Create your views here.       

@check_blocked
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


@check_blocked
def add_cart(request, variant_id):
    # Check if 'email' key exists in the session
    if 'email' not in request.session:
        return redirect('user:login') 

    email = request.session['email']
    user = Customers.objects.get(email=email)

    # Get product variant object based on variant_id
    product = get_object_or_404(Product_Variant, pk=variant_id)

    selected_rom = request.POST.get('selected_rom')
    
    # Create or get cart item for the user and product
    cart_item, created = Cart.objects.get_or_create(user_id=user, product_variant=product)

    # If cart item already exists, increment its quantity
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Remove the product from the wishlist
    try:
        wishlist = Wishlist.objects.get(user=user)
        wishlist.products.remove(product)
    except Wishlist.DoesNotExist:
        pass

    # Add success message
    messages.success(request, f" added to your cart.")

    # Return success response
    return redirect('user:index')






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
    messages.success(request, 'cart items have been successfully deleted.')
    # Redirect the user back to the cart page after deletion
    return redirect('shop_cart')

# views.py
def delete_all(request):
    email = request.session.get('email')  # Using get() to avoid KeyError if 'email' is not in session
    if email:
        user = Customers.objects.get(email=email)
        Cart.objects.filter(user_id=user).delete()
        messages.success(request, 'All cart items have been successfully deleted.')

        return render(request, "user_panel/shop_cart.html")
  



def update_cart_quantity(request):
    email = request.session.get('email')
    user = Customers.objects.get(email=email)
    if request.method == "POST":
        cart_item_id = request.POST.get("cart_item_id")
        quantity = int(request.POST.get("quantity"))
        print(quantity)
        try:
            cart_item = Cart.objects.get(pk=cart_item_id)
            cart_item.quantity = quantity
            cart_item.save()
            
            products=Cart.objects.all(user_id=user)
            items=CartItems(user=user,cart=products)
            items.save()
            
            # Calculate subtotal
            subtotal = cart_item.product_variant.sale_price * quantity

            return JsonResponse({"subtotal": subtotal, "quantity": quantity}, status=200)
        except Cart.DoesNotExist:
            return JsonResponse({"error": "Cart item not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)




