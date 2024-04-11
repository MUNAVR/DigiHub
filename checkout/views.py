from django.shortcuts import render
from .models import *
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from cart.models import Cart,CartItems
from products.models import Product_Variant,Products
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
    
    
    cart_items = Cart.objects.filter(user_id=user)
    
   
    subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
    shipping_charge = 100
    total = subtotal + shipping_charge 
    
    
    active_coupons = Coupon.objects.filter(active=True)

   
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
        "active_coupons": active_coupons 
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
            coupon_name = coupon.code  # Save the coupon name
        except Coupon.DoesNotExist:
            pass 
    else:
        coupon_name ="No Coupon"  # If no coupon is applied, set coupon_name to None

    checkout = Checkout.objects.create(user=user, subtotal=subtotal)

    # Create the order with the total amount and subtotal
    order = Order.objects.create(user=user, total_amount=total, subtotal=subtotal, coupon=coupon_name)

        
    
    for cart_item in cart_items:
        OrderProduct.objects.create(
            user=user,
            order=order,
            product_name=cart_item.product_variant.product.product_name,
            quantity=cart_item.quantity,
            price=cart_item.product_variant.sale_price
        )

   
    cart_items.delete()

    
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
        return redirect('checkout') 
    
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
                coupon_name = coupon.code  # Save the coupon name
            except Coupon.DoesNotExist:
                pass 
        else:
            coupon_name ="No Coupon"  # If no coupon is applied, set coupon_name to None

        
        checkout = Checkout.objects.create(user=user, subtotal=subtotal)
        checkout.save()
        latest_order=Order.objects.filter(user=user).order_by('-order_date').first()
        if latest_order and latest_order.total_amount == total and latest_order.subtotal == subtotal:
            # If details match, redirect back to checkout page
            pass
        else:
            # If details don't match, create a new order
            order = Order.objects.create(user=user, total_amount=total, subtotal=subtotal, payment_status="Failed", payment_method="Online",coupon=coupon_name)
            order.save()
            for cart_item in cart_items:
                OrderProduct.objects.create(
                user=user,
                order=order,
                product_name=cart_item.product_variant.product.product_name,
                quantity=cart_item.quantity,
                price=cart_item.product_variant.sale_price
        )
        
        order_id = Order.objects.order_by('-order_date').first()

        amount = total  # Example amount in paise, change as per your requirement
        currency = "INR"

        client = razorpay.Client(auth=("rzp_test_Os7R5CUHs9KARd", "dMgNLCLxwet33mAI6ok4uiQL"))

        payment = client.order.create({
            "amount": int(amount * 100),  # Convert to paise
            "currency": currency,
            "payment_capture": '1'  # Auto capture payment
        })

        email = request.session.get('email')
        user = Customers.objects.get(email=email)   
        
        
        cart_items = Cart.objects.filter(user_id=user)
        
    
        subtotal = sum(cart_item.product_variant.sale_price * cart_item.quantity for cart_item in cart_items)
        shipping_charge = 100
        total = subtotal + shipping_charge 
        
        
        active_coupons = Coupon.objects.filter(active=True)

    
        used_coupons = CouponUsage.objects.filter(user=user).values_list('coupon', flat=True)
        active_coupons = active_coupons.exclude(id__in=used_coupons)

        add1 = Address1.objects.filter(user=user)
        add2 = Address2.objects.filter(user=user)

        context = {
            "payment_details": {
                "id": payment['id'],  
                "amount": int(amount * 100),  # Convert to paise
                "currency": currency,
                "key": "rzp_test_Os7R5CUHs9KARd", 
                "email": email, 
                "coupon":coupon_id,
            },
        "cart": cart_items,
        "subtotal": subtotal,
        "total": total,
        "add1": add1,
        "add2": add2,
        "active_coupons": active_coupons,
        "order_id":order_id
            
        }
        return render(request, "user_panel/checkout.html", context)
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
       
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        email = request.POST.get('email')
        print(email)
        coupon_id = request.POST.get('coupon_id')
        order_id_str = request.POST.get('order_id')  # Get the order ID as a string
        order_id = int(order_id_str.split('(')[1].split(')')[0])   

        try:
            user = Customers.objects.get(email=email)
        except Customers.DoesNotExist:
            return HttpResponse('Invalid email', status=400)  
        
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
                pass 
        
        
        checkout = Checkout(user=user, subtotal=subtotal)
        checkout.save()

        order = Order.objects.get(id=order_id)
        order.payment_status = "paid"
        order.save()
        
        cart_items.delete()

        od = Order.objects.filter(user=user).order_by('-order_date').first()

        
        context = {
            "total_amount": total,
            "order": od,
        }

        
        return render(request, 'user_panel/order_succes.html', context)
    else:
        return render(request, 'user_panel/checkout.html')



from django.db import transaction

@transaction.atomic
def wallet_payment(request):
    email = request.session.get('email')
    user = Customers.objects.get(email=email)
    
    
    try:
        wallet = Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        messages.error(request, "You don't have a wallet. Please add funds to your wallet first.")
        return redirect('wallet') 

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
                coupon_name = coupon.code  # Save the coupon name
            except Coupon.DoesNotExist:
                pass 
    else:
            coupon_name ="No Coupon" 

    # Check if the wallet balance is sufficient for the order
    if wallet.balance < total:
        messages.error(request, "Insufficient funds in your wallet. Please add funds to your wallet.")
        return redirect('wallet') 
    
    order = Order(user=user, total_amount=total, payment_method="wallet", payment_status="paid",subtotal=subtotal,coupon=coupon_name)
    order.save()

    for cart_item in cart_items:
            OrderProduct.objects.create(
            user=user,
            order=order,
            product_name=cart_item.product_variant.product.product_name,
            quantity=cart_item.quantity,
            price=cart_item.product_variant.sale_price
        )

    wallet.balance -= total
    wallet.save()
    transaction = Transaction.objects.create(wallet=wallet, amount=total, transaction_type="Debit")

    od = Order.objects.filter(user=user).order_by('-order_date').first()

    context = {
        "total_amount": total,
        "order": od,
        "transaction": transaction  
    }
    return render(request, "user_panel/order_succes.html", context)




from django.core.paginator import Paginator

def all_orders(request):
    if 'email' not in request.session:
        return redirect('user:login')
    
    current_email = request.session['email']
    user = Customers.objects.get(email=current_email)

    order_list = Order.objects.filter(user=user).order_by('-order_date')
    
    paginator = Paginator(order_list, 10)  

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
        
        return HttpResponse("Customer not found")
    except Order.DoesNotExist:
        
        return HttpResponse("Order not found")
    except OrderAddress.DoesNotExist:
        
        return HttpResponse("Order address not found")

from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate
from django.template.loader import render_to_string
from django.utils.safestring import SafeString
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors


def generate_pdf_invoice(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return HttpResponse("Order not found")

    
    email = request.session.get('email')
    user = Customers.objects.get(email=email)
    address = get_object_or_404(OrderAddress, order=order)

    # Define filename for the PDF
    pdf_filename = f"invoice_{order_id}_{user.first_name.replace(' ', '_')}.pdf"

    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'

    # Initialize buffer and document
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(name='CenteredHeading', alignment=1, fontName='Helvetica-Bold', fontSize=16)
    paragraph_style = ParagraphStyle(name='Normal', fontName='Helvetica', fontSize=12, leading=15)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ])

    
    content = []

    content.append(Paragraph("Invoice", header_style))
    content.append(Paragraph("<br/><br/>", paragraph_style))

   
    company_details = [
        "DigiHub",
        "Location: Maradu, Kochi", 
        "Ernakulam, Kerala",
        "Phone Number: 9562978458"
    ]
    company_details_paragraphs = [Paragraph(detail, paragraph_style) for detail in company_details]

    customer_details = [
        f"Customer: {user.first_name}",
        f"Email: {user.email}",
        f"Delivery Address: {address.address}, {address.locality}, {address.district}, {address.state}, {address.pincode}"
    ]
    customer_details_paragraphs = [Paragraph(detail, paragraph_style) for detail in customer_details]

    # Add company and customer details in two separate columns
    data = [
        [company_details_paragraphs[0], customer_details_paragraphs[0]],
        [company_details_paragraphs[1], customer_details_paragraphs[1]],
        [company_details_paragraphs[2], customer_details_paragraphs[2]]
    ]
    table = Table(data, colWidths=[300, 300])
    table.setStyle(table_style)
    content.append(table)

    
    products = OrderProduct.objects.filter(order=order)

    
    product_data = [['Product Name', 'Quantity', 'Price']]
    for product in products:
        product_data.append([product.product_name, product.quantity, product.price])
    product_table = Table(product_data)
    product_table.setStyle(table_style)
    content.append(product_table)

    # Add a line gap after product details list
    content.append(Paragraph("<br/><br/>", paragraph_style))

   
    subtotal_paragraph = Paragraph(f"Subtotal: ₹ {order.subtotal}", paragraph_style)
    content.append(subtotal_paragraph)

   
    shipping_charge_paragraph = Paragraph("Shipping Charge: ₹ 100", paragraph_style)
    content.append(shipping_charge_paragraph)

    
    if order.coupon != "No Coupon":
        used_coupon_paragraph = Paragraph(f"Used Coupon: {order.coupon}", paragraph_style)
        content.append(used_coupon_paragraph)

    
    grand_total_paragraph = Paragraph(f"Grand Total: ₹ {order.total_amount}", paragraph_style)
    content.append(grand_total_paragraph)

    # Build PDF
    doc.build(content)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response



def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        if order.order_status == 'Cancelled':
            messages.error(request, 'Order has already been cancelled.')
        elif order.order_status == 'Pending' and order.payment_status == 'Pending':
            order.order_status = 'Cancelled'
            order.save()
            return_products_to_inventory(order)  
            messages.success(request, 'Order has been cancelled successfully.')
        elif order.payment_method in ['Online', 'wallet']:
            refund_to_wallet(request, order)
            order.order_status = 'Cancelled'
            order.save()
            return_products_to_inventory(order) 
        else:
            messages.error(request, 'Order cannot be cancelled at this time.')
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
    return redirect('all_orders')

def return_products_to_inventory(order):
    
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
                
                order.order_status = 'Returned'
                order.save()

                
                order_products = OrderProduct.objects.filter(order=order)
                for order_product in order_products:
                    product_name = order_product.product_name
                    product_variant = Product_Variant.objects.get(product__product_name=product_name)
                    product_variant.stock += order_product.quantity
                    product_variant.save()

               
                user_wallet = Wallet.objects.get(user=order.user)
                user_wallet.balance += order.total_amount
                user_wallet.save()

               
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
    order = Order.objects.get(id=id)
    user = Customers.objects.get(email=email)
    latest_order_address = OrderAddress.objects.filter(user=user).order_by('-order__order_date').first()
    latest_order_address.order=order
    latest_order_address.save()
    return redirect('user:index')


def coutinue_payment(request,id):

    email = request.session.get('email')
    user = Customers.objects.get(email=email)

    order = get_object_or_404(Order, id=id)
    subtotal=order.subtotal
    total=order.total_amount

    add1 = Address1.objects.filter(user=user)
    add2 = Address2.objects.filter(user=user)

    active_coupons = Coupon.objects.filter(active=True)
    used_coupons = CouponUsage.objects.filter(user=user).values_list('coupon', flat=True)
    active_coupons = active_coupons.exclude(id__in=used_coupons)

    cart_items = OrderProduct.objects.filter(order=order)
    product_names = set(order_product.product_name for order_product in cart_items)
    products = Products.objects.filter(product_name__in=product_names)
    product_images = [] 
    
   
    for product in products:
        
        product_variant = Product_Variant.objects.filter(product=product).first()
        
       
        if product_variant:
            product_images.append(product_variant.thumbnail_image.url)

    context = {
        "cart": cart_items,
        "subtotal": subtotal,
        "total": total,
        "add1": add1,
        "add2": add2,
        "active_coupons": active_coupons,
        "product_images": product_images, 
    }
    return render(request,"user_panel/checkout.html",context)   