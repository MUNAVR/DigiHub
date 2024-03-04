from django.shortcuts import render
from .models import *
from django.shortcuts import render, redirect
from django.http import JsonResponse
from cart.models import Cart,CartItems
from products.models import Product_Variant
from django.db.models import Sum
from django.db.models import Sum, F
from app_1.models import Address1,Customers,Address2



def checkout_page(request):
    email = request.session.get('email')
    user = Customers.objects.get(email=email)
    
    # Retrieve cart items for the user's cart
    cart_items = Cart.objects.filter(user_id=user)
    
    # Calculate subtotal for all items in the cart
    subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
    shipping_charge= 100
    total=subtotal + 100 
    add1=Address1.objects.filter(user=user)
    add2=Address2.objects.filter(user=user)
    context = {
        "cart": cart_items,
        "subtotal": subtotal,
        "total":total,
        "add1":add1,
        "add2":add2
    }
    return render(request, 'user_panel/checkout.html', context)


from django.utils import timezone

def place_order(request):
    # Get the user
    email = request.session.get('email')
    user = Customers.objects.get(email=email)
    
    # Get the cart items for the user
    cart_items = Cart.objects.filter(user_id=user)
    
    # Calculate subtotal
    subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
    
    # Calculate total amount including shipping charge
    shipping_charge = 100
    total_amount = subtotal + shipping_charge
    
    # Create the order instance
    Order.objects.create(user=user, total_amount=total_amount, order_date=timezone.now())
    order=Order.objects.all(user=user)
    context={
        "order":order
    }
    
    # Redirect or render a success message
    return render(request, 'order_success.html',context)


    

