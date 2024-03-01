from django.shortcuts import render
from .models import *
from django.shortcuts import render, redirect
from django.http import JsonResponse
from cart.models import Cart
from products.models import Product_Variant
# Create your views here.

from django.db.models import Sum

from django.db.models import Sum, F

def calculate_total_amount(cart_items):
    # Annotate each cart item with the product of sale price and quantity
    cart_items = cart_items.annotate(subtotal=F('Product_Variant__sale_price') * F('quantity'))
    # Calculate the total amount by summing up the annotated values
    total_amount = cart_items.aggregate(total=Sum('subtotal'))['total']
    return total_amount if total_amount is not None else 0

def store_cart_data(request):
    if 'email' not in request.session:
        return redirect('user:login')
    
    email = request.session['email']
    user = Customers.objects.get(email=email)
    if request.method == "POST" and request.is_ajax():

        cart_items = Cart.objects.filter(user_id=user)
        total_amount = calculate_total_amount(cart_items)
        request.session['cart_items'] = list(cart_items.values_list('id', flat=True))
        request.session['total_amount'] = total_amount
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)


def checkout_page(request):
    cart_item_ids = request.session.get('cart_items')
    total_amount = request.session.get('total_amount', 0)
    print(cart_item_ids)
    if cart_item_ids:
        cart_items = Cart.objects.filter(id__in=cart_item_ids)
        return render(request, 'user_panel/checkout.html', {'cart_items': cart_items, 'total_amount': total_amount})
    else:
        return redirect('shop_cart')