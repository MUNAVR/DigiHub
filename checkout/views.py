from django.shortcuts import render
from .models import *
from django.shortcuts import render, redirect, reverse
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

    # Create checkout object
    checkout = Checkout.objects.create(user=user, subtotal=subtotal)

    # Create order object
    order = Order.objects.create(user=user, total_amount=total,subtotal=subtotal)
        
    # Save order products
    for cart_item in cart_items:
        OrderProduct.objects.create(
            user=user,
            order=order,
            product_name=cart_item.product_variant.product.product_name,
            quantity=cart_item.quantity,
            price=cart_item.product_variant.sale_price
        )

    # Clear the cart items after placing the order
    cart_items.delete()

    # Fetch order details
    od = Order.objects.filter(user=user).order_by('-order_date').first()

    context = {
        "total_amount": total,
        "order": od,
    }
    return render(request, "user_panel/order_succes.html", context)



@csrf_exempt
def save_order_address(request):
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        email = request.session.get('email')
        user = Customers.objects.get(email=email)
        selected_address_id = request.POST.get('selected_address_id')
        print(selected_address_id)
        if selected_address_id:
            try:
                # Fetch the address based on selected_address_id
                address = None
                first= "address1"
                second="address2"
                
                print(user)
                print("2")
                if selected_address_id == first:
                    print("3")
                    address = Address1.objects.get(user=user)
                    print(address)
                elif selected_address_id == second:
                    address = Address2.objects.get(user=user)
                    print(address)

                print("5")
                if address:
                    order = Order.objects.filter(user=user).latest('order_date')
                    print(order)
                    if order:
                        # Create OrderAddress object
                        order_address = OrderAddress.objects.create(
                            order=order,
                            user=user,
                            address=address.address,
                            locality=address.locality,
                            state=address.state,
                            district=address.district,
                            pincode=address.pincode
                        )
                        order_address.save()
                        print(order_address)
                        return JsonResponse({'message': 'Address saved successfully'}, status=200)
                    else:
                        return JsonResponse({'error': 'No order found for the user'}, status=400)
            except (Address1.DoesNotExist, Address2.DoesNotExist):
                pass
        return JsonResponse({'error': 'Address not found'}, status=400)
    else:
            # Default to saving Address1 if no address is selected
            try:
                address = Address1.objects.get(user=user)
                order = Order.objects.filter(user=user).latest('order_date')
                if order:
                    order_address = OrderAddress.objects.create(
                        order=order,
                        user=user,
                        address=address.address,
                        locality=address.locality,
                        state=address.state,
                        district=address.district,
                        pincode=address.pincode
                    )
                    order_address.save()
                    return JsonResponse({'message': 'Address saved successfully'}, status=200)
                else:
                    return JsonResponse({'error': 'No order found for the user'}, status=400)
            except Address1.DoesNotExist:
                return JsonResponse({'error': 'Default address (Address1) not found'}, status=400)
            



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

        order = Order(user=user, total_amount=total, payment_status="paid", payment_method="Online",subtotal=subtotal)
        order.save()

        for cart_item in cart_items:
            OrderProduct.objects.create(
            user=user,
            order=order,
            product_name=cart_item.product_variant.product.product_name,
            quantity=cart_item.quantity,
            price=cart_item.product_variant.sale_price
        )

        # Clear the cart after placing the order
        cart_items.delete()

        od = Order.objects.filter(user=user).order_by('-order_date').first()

        # Pass context data to the success template
        context = {
            "total_amount": total,
            "order": od,
        }

        # Render the success template with context data
        return render(request, 'user_panel/order_succes.html', context)
    else:
        return render(request, 'user_panel/checkout.html')



@csrf_exempt
def handle_razorpay_failure(request):
    if request.method == "POST":
        # Extract payment information from the POST request
        razorpay_order_id = request.POST.get('razorpay_order_id')
        email = request.POST.get('email')
        coupon_id = request.POST.get('coupon_id')

        try:
            # Retrieve the user based on the email
            user = Customers.objects.get(email=email)
        except Customers.DoesNotExist:
            return HttpResponse('Invalid email', status=400)

        # Retrieve cart items for the user
        cart_items = Cart.objects.filter(user_id=user)

        # Calculate total amount including shipping charge
        subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
        shipping_charge = 100
        total = subtotal + shipping_charge

        # Apply coupon logic if coupon ID is provided
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id, active=True)
                discount_amount = total * (coupon.discount / 100)
                total -= discount_amount
            except Coupon.DoesNotExist:
                pass  # Handle the case where the coupon does not exist

        # Update the order status to failed
        order = Order(user=user, total_amount=total, payment_status="failed", payment_method="Online",order_status="failed")
        order.save()

        # Additional logic for handling failed payments can be added here
        
        # Add a message for the user
        messages.error(request, 'Payment failed. Please try again.')

        # Redirect to the appropriate page
        return render(request,'user_panel/failure.html')


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
    order = Order(user=user, total_amount=total, payment_method="wallet", payment_status="paid",subtotal=subtotal)
    order.save()

    for cart_item in cart_items:
            OrderProduct.objects.create(
            user=user,
            order=order,
            product_name=cart_item.product_variant.product.product_name,
            quantity=cart_item.quantity,
            price=cart_item.product_variant.sale_price
        )
    # Deduct payment amount from the wallet balance and create a transaction record
    wallet.balance -= total
    wallet.save()
    transaction = Transaction.objects.create(wallet=wallet, amount=total, transaction_type="Debit")

    # Fetch order details
    od = Order.objects.filter(user=user).order_by('-order_date').first()

    context = {
        "total_amount": total,
        "order": od,
        "transaction": transaction  # Pass transaction details to the template
    }
    return render(request, "user_panel/order_succes.html", context)




from django.core.paginator import Paginator

def all_orders(request):
    if 'email' not in request.session:
        return redirect('user:login')
    
    current_email = request.session['email']
    user = Customers.objects.get(email=current_email)

    order_list = Order.objects.filter(user=user).order_by('-order_date')
    
    paginator = Paginator(order_list, 10)  # Show 10 orders per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    return render(request, "user_panel/all_orders.html", context)




def order_details(request, id):
    try:
        email = request.session.get('email')
        user = Customers.objects.get(email=email)
        order = get_object_or_404(Order, id=id)
        addrss = get_object_or_404(OrderAddress, order=order)
        products = OrderProduct.objects.filter(order=order)
        cart_items = Cart.objects.filter(user_id=user)
        subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
        context = {
            "user": user,
            "order": order,
            "add": addrss,
            "product": products,
        }
        return render(request, "user_panel/order_details.html", context)
    except Customers.DoesNotExist:
        # Handle case where customer doesn't exist
        return HttpResponse("Customer not found")
    except Order.DoesNotExist:
        # Handle case where order doesn't exist
        return HttpResponse("Order not found")
    except OrderAddress.DoesNotExist:
        # Handle case where order address doesn't exist
        return HttpResponse("Order address not found")




def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        if order.order_status == 'Cancelled':
            messages.error(request, 'Order has already been cancelled.')
        elif order.order_status == 'Pending' and order.payment_status == 'Pending':
            order.order_status = 'Cancelled'
            order.save()
            return_products_to_inventory(order)  # Return products to inventory
            messages.success(request, 'Order has been cancelled successfully.')
        elif order.payment_method in ['Online', 'wallet']:
            refund_to_wallet(request, order)
            order.order_status = 'Cancelled'
            order.save()
            return_products_to_inventory(order)  # Return products to inventory
        else:
            messages.error(request, 'Order cannot be cancelled at this time.')
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
    return redirect('all_orders')

def return_products_to_inventory(order):
    # Return products to inventory and update quantity
    order_products = OrderProduct.objects.filter(order=order)
    for order_product in order_products:
        product_name = order_product.product_name
        product_variant = Product_Variant.objects.get(product__product_name=product_name)
        product_variant.stock += order_product.quantity
        product_variant.save()

def return_order(request, order_id):
    if request.method == 'GET':
        try:
            order = Order.objects.get(id=order_id)
            if order.order_status == 'Completed':
                # Update order status to 'Returned'
                order.order_status = 'Returned'
                order.save()

                # Return products to inventory and update quantity
                order_products = OrderProduct.objects.filter(order=order)
                for order_product in order_products:
                    product_name = order_product.product_name
                    product_variant = Product_Variant.objects.get(product__product_name=product_name)
                    product_variant.stock += order_product.quantity
                    product_variant.save()

                # Refund amount to user's wallet
                user_wallet = Wallet.objects.get(user=order.user)
                user_wallet.balance += order.total_amount
                user_wallet.save()

                # Record wallet transaction
                Transaction.objects.create(
                    wallet=user_wallet,
                    amount=order.total_amount,
                    transaction_type='Credit',
                )

                messages.success(request, 'Order returned successfully.')
            else:
                messages.error(request, 'Cannot return order as it is not completed.')
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
    return redirect(reverse('all_orders'))


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

def continue_shoping(request,id):
    email = request.session.get('email')
    order=Order.objects.get(id=id)
    user = Customers.objects.get(email=email)
    latest_order_address = OrderAddress.objects.filter(user=user).order_by('-order__order_date').first()
    latest_order_address.order=order
    latest_order_address.save()
    return redirect('user:index')


