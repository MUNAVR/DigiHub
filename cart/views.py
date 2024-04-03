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
        return redirect('user:login')  

    
    email = request.session['email']

   
    user = Customers.objects.get(email=email)

    cart_items = Cart.objects.filter(user_id=user)

    context = {
        'cart_items': cart_items,
    }

    return render(request, "user_panel/shop_cart.html", context)


@check_blocked
def add_cart(request, variant_id):
    
    if 'email' not in request.session:
        return redirect('user:login') 

    email = request.session['email']
    user = Customers.objects.get(email=email)

    
    product = get_object_or_404(Product_Variant, pk=variant_id)

    # Check if stock is less than or equal to 1
    if product.stock <= 1:
        messages.error(request, f" is out of stock.")
        return redirect('user:index')

    selected_rom = request.POST.get('selected_rom')
    
    
    cart_item, created = Cart.objects.get_or_create(user_id=user, product_variant=product)

    # If cart item already exists, increment its quantity
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Decrease stock in the database
    product.stock -= 1 
    product.save()

    # Remove the product from the wishlist
    try:
        wishlist = Wishlist.objects.get(user=user)
        wishlist.products.remove(product)
    except Wishlist.DoesNotExist:
        pass

   
    messages.success(request, f"added to your cart.")

    
    return redirect('user:index')


def delete_cart_item(request, cart_item_id):
    
    try:
        cart_item = Cart.objects.get(pk=cart_item_id)
    except Cart.DoesNotExist:
       
        return redirect('shop_cart')

    
    product_variant = cart_item.product_variant

    
    product_variant.stock += cart_item.quantity
    product_variant.save()

    
    cart_item.delete()

    messages.success(request, 'Cart item has been successfully deleted.')

    
    return redirect('shop_cart')


def delete_all(request):
    email = request.session.get('email') 
    if email:
        user = Customers.objects.get(email=email)
        
    
        cart_items = Cart.objects.filter(user_id=user)
        
        # Increment the stock quantity of each product variant
        for cart_item in cart_items:
            product_variant = cart_item.product_variant
            product_variant.stock += cart_item.quantity
            product_variant.save()
        
        
        cart_items.delete()
        
        messages.success(request, 'All cart items have been successfully deleted.')

    return redirect('shop_cart')



def update_cart_quantity(request):
    email = request.session.get('email')
    user = Customers.objects.get(email=email)

    if request.method == "POST":
        cart_item_id = request.POST.get("cart_item_id")
        quantity = int(request.POST.get("quantity"))
        
        try:
            cart_item = Cart.objects.get(pk=cart_item_id)

            # Check if requested quantity exceeds available stock
            if quantity > cart_item.product_variant.stock:
                stock_quantity = cart_item.product_variant.stock
                return JsonResponse({"error": "Requested quantity exceeds available stock", "stock_quantity": stock_quantity}, status=400)
            
            
            quantity_diff = quantity - cart_item.quantity

            # Update cart item quantity
            cart_item.quantity = quantity
            cart_item.save()

            # Update product stock quantity
            product = cart_item.product_variant
            product.stock -= quantity_diff
            product.save()

            
            subtotal = cart_item.product_variant.sale_price * quantity

            return JsonResponse({"subtotal": subtotal, "quantity": quantity}, status=200)
        except Cart.DoesNotExist:
            return JsonResponse({"error": "Cart item not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)






