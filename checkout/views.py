from django.shortcuts import render
from .models import *
from django.shortcuts import render, redirect
from django.http import JsonResponse
from cart.models import Cart,CartItems
from products.models import Product_Variant
from django.db.models import Sum
from django.db.models import Sum, F
from app_1.models import Address1,Customers,Address2
from django.utils import timezone
from django.contrib import messages
import razorpay
from django.db.models import Sum
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
import uuid
from wallet.models import Wallet,Transaction
from coupon.models import Coupon,CouponUsage
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404


def checkout_page(request):
    email = request.session.get('email')
    user = Customers.objects.get(email=email)
    
    # Retrieve cart items for the user's cart
    cart_items = Cart.objects.filter(user_id=user)
    
    # Calculate subtotal for all items in the cart
    subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
    shipping_charge = 100
    total = subtotal + shipping_charge 
    
    # Retrieve active coupons
    active_coupons = Coupon.objects.filter(active=True)

    # Exclude coupons that have been used by the user
    used_coupons = CouponUsage.objects.filter(user=user).values_list('coupon', flat=True)
    active_coupons = active_coupons.exclude(id__in=used_coupons)

    add1 = Address1.objects.filter(user=user)
    add2 = Address2.objects.filter(user=user)
    
    context = {
        "cart": cart_items,
        "subtotal": subtotal,
        "total": total,
        "add1": add1,
        "add2": add2,
        "active_coupons": active_coupons  # Pass active coupons to the template
    }
    return render(request, 'user_panel/checkout.html', context)



from django.core.exceptions import ObjectDoesNotExist

def apply_coupon(request):
    email = request.session.get('email')
    if not email:   
        return JsonResponse({'error': 'Session email is missing'}, status=400)

    user = get_object_or_404(Customers, email=email)
    
    cart_items = Cart.objects.filter(user_id=user)
    if not cart_items.exists():
        return JsonResponse({'error': 'Cart is empty'}, status=400)
    
    subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
    shipping_charge = 100
    total = subtotal + shipping_charge 

    if request.method == 'POST':
        coupon_id = request.POST.get('coupon_id')
        if not coupon_id:
            return JsonResponse({'error': 'Coupon ID is missing'}, status=400)

        try:
            coupon = Coupon.objects.get(id=coupon_id, active=True)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Invalid coupon ID'}, status=400)

        # Check if the coupon has already been applied by the user
        if CouponUsage.objects.filter(coupon=coupon, user=user).exists():
            return JsonResponse({'error': 'Coupon has already been used by this user'}, status=400)

        discounted_total = total * (1 - coupon.discount / 100)
        request.session['coupon_id'] = coupon_id
        
        # Create CouponUsage record to track coupon usage by the user
        CouponUsage.objects.create(coupon=coupon, user=user)

        return JsonResponse({'discounted_total': discounted_total})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


  

    
def place_order(request):
    email = request.session.get('email')
    user = Customers.objects.get(email=email)
    cart_items = Cart.objects.filter(user_id=user)

    subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
    shipping_charge = 100
    total = subtotal + shipping_charge

    coupon_id = request.session.get('coupon_id')

    if coupon_id:
        # Apply coupon logic here
        try:
            coupon = Coupon.objects.get(id=coupon_id, active=True)
            discount_amount = total * (coupon.discount / 100)
            total -= discount_amount
        except Coupon.DoesNotExist:
            pass 
    # Create checkout and order objects
    checkout = Checkout(user=user, subtotal=subtotal)
    checkout.save()

    order = Order(user=user, total_amount=total)
    order.save()

    # Fetch order details
    od = Order.objects.filter(user=user).order_by('-order_date').first()
    addrss = Address1.objects.get(user=user)

    context = {
        "total_amount": total,
        "order": od,
        "add": addrss
    }
    return render(request, "user_panel/order_succes.html", context)



def razorpay_payment(request):
    email = request.session.get('email')
    if email is None:
        return redirect('checkout')  # Redirect to checkout page if email is not in session
    
    try:
        user = Customers.objects.get(email=email)
        cart_items = Cart.objects.filter(user_id=user)

        subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
        shipping_charge = Decimal('100')  # Convert to Decimal
        total = subtotal + shipping_charge

        coupon_id = request.session.get('coupon_id')

        if coupon_id:
            # Apply coupon logic here
            try:
                coupon = Coupon.objects.get(id=coupon_id, active=True)
                discount_amount = total * (coupon.discount / 100)
                total -= discount_amount
            except Coupon.DoesNotExist:
                pass 
        amount = total  # Example amount in paise, change as per your requirement
        currency = "INR"

        client = razorpay.Client(auth=("rzp_test_Os7R5CUHs9KARd", "dMgNLCLxwet33mAI6ok4uiQL"))

        payment = client.order.create({
            "amount": int(amount * 100),  # Convert to paise
            "currency": currency,
            "payment_capture": '1'  # Auto capture payment
        })
        print(coupon_id)
        context = {
            "payment_details": {
                "id": payment['id'],  # Use the generated order ID
                "amount": int(amount * 100),  # Convert to paise
                "currency": currency,
                "key": "rzp_test_Os7R5CUHs9KARd", 
                "email": email, 
                "coupon":coupon_id,
            }
        }
        return render(request, "user_panel/razorpay.html", context)
    except Customers.DoesNotExist:
        messages.error(request, 'Customer not found.')
    except Exception as e:
        messages.error(request, f'Razorpay payment failed: {str(e)}')
    
    return redirect('checkout') 


from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse

@csrf_exempt
def handle_razorpay_success(request):
    if request.method == "POST":
        # Extract payment information from the POST request
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        email = request.POST.get('email')
        print(email)
        coupon_id = request.POST.get('coupon_id')

        print(coupon_id)    

        # Add your logic to mark the order as paid or any other necessary actions
        # For example, create a new order and save it to the database
        try:
            user = Customers.objects.get(email=email)
        except Customers.DoesNotExist:
            return HttpResponse('Invalid email', status=400)  # Return a 400 response for an invalid email
        
        cart_items = Cart.objects.filter(user_id=user)

        subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
        shipping_charge = 100
        total = subtotal + shipping_charge

        
        if coupon_id:
            # Apply coupon logic here
            try:
                coupon = Coupon.objects.get(id=coupon_id, active=True)
                discount_amount = total * (coupon.discount / 100)
                total -= discount_amount
            except Coupon.DoesNotExist:
                pass  # Handle the case where the coupon does not exist
        
        # Create checkout and order objects
        checkout = Checkout(user=user, subtotal=subtotal)
        checkout.save()

        order = Order(user=user, total_amount=total, payment_status="paid", payment_method="Online")
        order.save()

        # Clear the cart after placing the order
        cart_items.delete()

        od = Order.objects.filter(user=user).order_by('-order_date').first()
        addrss = Address1.objects.get(user=user)

        # Pass context data to the success template
        context = {
            "total_amount": total,
            "order": od,
            "add": addrss
        }

        # Render the success template with context data
        return render(request, 'user_panel/order_succes.html', context)
    else:
        return render(request, 'user_panel/checkout.html')



def handle_razorpay_failure(request):
    # Add your logic for handling failed payments
    messages.error(request, 'Payment failed. Please try again.')
    return redirect('user_panel:checkout_page')


from django.db import transaction

@transaction.atomic
def wallet_payment(request):
    email = request.session.get('email')
    user = Customers.objects.get(email=email)
    
    # Check if the user has a wallet
    try:
        wallet = Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        messages.error(request, "You don't have a wallet. Please add funds to your wallet first.")
        return redirect('wallet')  # Redirect to the wallet page

    # Calculate total amount for the order
    cart_items = Cart.objects.filter(user_id=user)
    subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
    shipping_charge = 100
    total = subtotal + shipping_charge
    
    coupon_id = request.session.get('coupon_id')

    if coupon_id:
        # Apply coupon logic here
        try:
            coupon = Coupon.objects.get(id=coupon_id, active=True)
            discount_amount = total * (coupon.discount / 100)
            total -= discount_amount
        except Coupon.DoesNotExist:
            pass 

    # Check if the wallet balance is sufficient for the order
    if wallet.balance < total:
        messages.error(request, "Insufficient funds in your wallet. Please add funds to your wallet.")
        return redirect('wallet')  # Redirect to the wallet page
    
    # Proceed with creating the order
    order = Order(user=user, total_amount=total, payment_method="wallet", payment_status="paid")
    order.save()

    # Deduct payment amount from the wallet balance and create a transaction record
    wallet.balance -= total
    wallet.save()
    transaction = Transaction.objects.create(wallet=wallet, amount=total, transaction_type="Debit")

    # Fetch order details
    od = Order.objects.filter(user=user).order_by('-order_date').first()
    addrss = Address1.objects.get(user=user)

    context = {
        "total_amount": total,
        "order": od,
        "add": addrss,
        "transaction": transaction  # Pass transaction details to the template
    }
    return render(request, "user_panel/order_succes.html", context)





def all_orders (request):
    if 'email' not in request.session:
        return redirect('user:login')
    
    current_email = request.session['email']
    user = Customers.objects.get(email = current_email)

    order = Order.objects.filter(user=user).order_by('-order_date')
    context={
        "order":order
    }
    return render(request,"user_panel/all_orders.html",context)



def order_details(request, id):
    email = request.session.get('email')
    user = Customers.objects.get(email=email)
    addrss = Address1.objects.get(user=user)
    order = Order.objects.get(id=id)
    
    # Fetch the Checkout object
    checkout = Checkout.objects.filter(user=user)

    context = {
        "checkout":checkout,
        "user": user,
        "order": order,
        "add": addrss,
       
    }
    return render(request, "user_panel/order_details.html", context)



def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        
        if order.order_status == 'Cancelled':
            messages.error(request, 'Order has already been cancelled.')
        elif order.order_status == 'Pending' and order.payment_status == 'Pending':
            order.order_status = 'Cancelled'
            order.save()
            messages.success(request, 'Order has been cancelled successfully.')
        elif order.payment_method in ['Online', 'wallet']:
            refund_to_wallet(request, order)
            order.order_status = 'Cancelled'
            order.save()
            
        else:
            messages.error(request, 'Order cannot be cancelled at this time.')
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')

    return redirect('all_orders')

def refund_to_wallet(request, order):
    try:
        wallet = Wallet.objects.get(user=order.user)
        transaction = Transaction.objects.create(
            wallet=wallet,
            amount=order.total_amount,
            transaction_type='Credit',
        )
        wallet.balance += order.total_amount
        wallet.save()
        transaction.save()
        messages.success(request, 'Order has been cancelled successfully. Amount refunded to wallet.')
    except Wallet.DoesNotExist:
        messages.error(request, 'Wallet not found for the user.')


  # Redirect to order details page

