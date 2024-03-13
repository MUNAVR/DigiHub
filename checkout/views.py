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





def checkout_page(request):
    email = request.session.get('email')
    user = Customers.objects.get(email=email)
    
    # Retrieve cart items for the user's cart
    cart_items = Cart.objects.filter(user_id=user)
    
    # Calculate subtotal for all items in the cart
    subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
    shipping_charge = 100
    total = subtotal + shipping_charge 
    add1 = Address1.objects.filter(user=user)
    add2 = Address2.objects.filter(user=user)
    
    context = {
        "cart": cart_items,
        "subtotal": subtotal,
        "total": total,
        "add1": add1,
        "add2": add2
    }
    return render(request, 'user_panel/checkout.html', context)

def place_order(request):
    email = request.session.get('email')
    user = Customers.objects.get(email=email)
    cart_items = Cart.objects.filter(user_id=user)

    subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
    shipping_charge = 100
    total = subtotal + shipping_charge

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
    
    print(email)
    user = Customers.objects.get(email=email)
    cart_items = Cart.objects.filter(user_id=user)

    subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
    shipping_charge = Decimal('100')  # Convert to Decimal
    total = subtotal + shipping_charge
    amount = total  # Example amount in paise, change as per your requirement
    currency = "INR"

    client = razorpay.Client(auth=("rzp_test_Os7R5CUHs9KARd", "dMgNLCLxwet33mAI6ok4uiQL"))

    payment = client.order.create({
        "amount": int(amount * 100),  # Convert to paise
        "currency": currency,
        "payment_capture": '1'  # Auto capture payment
    })

    context = {
        "payment_details": {
            "id": payment['id'],  # Use the generated order ID
            "amount": int(amount * 100),  # Convert to paise
            "currency": currency,
            "key": "rzp_test_Os7R5CUHs9KARd", 
            "email": email # Replace with your Razorpay key
        }
    }
    return render(request, "user_panel/razorpay.html", context)


@csrf_exempt
def handle_razorpay_success(request):
    print('yep reach here')
    if request.method == "POST":
        # Extract payment information from the POST request
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        email = request.POST.get('email')
        # Add your logic to mark the order as paid or any other necessary actions
        # For example, create a new order and save it to the database
        
        print(email)
        user = Customers.objects.get(email=email)
        cart_items = Cart.objects.filter(user_id=user)

        subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
        shipping_charge = 100
        total = subtotal + shipping_charge

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
        return render(request,'user_panel/checkout.html')

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
        print(order)
        # Check if the order is cancellable
        if order.order_status == 'Cancelled':
            messages.error(request, 'Order has already been cancelled.')
        elif order.order_status == 'Pending' and order.payment_status == 'Pending':
            # Update order status to 'Cancelled'
            order.order_status = 'Cancelled'
            order.save()

            # Refund the amount based on payment method
        elif order.payment_method == 'Online' or order.payment_method == 'wallet':
                refund_to_wallet(request, order)
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

