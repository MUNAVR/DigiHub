from django.shortcuts import render
from .models import *
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render,redirect
from products.models import Products, Product_Variant
from category.models import Brand
from django.http import HttpResponse
from decimal import Decimal
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from app_1.decorators import check_blocked
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from decimal import Decimal
# Create your views here.

@check_blocked
def wallet(request):
    current_email = request.session['email']
    user = Customers.objects.get(email=current_email)

    try:
        # Retrieve the user's wallet
        wallet = Wallet.objects.get(user=user)
        
        # Retrieve the user's transaction history
        transactions = Transaction.objects.filter(wallet=wallet).order_by('-date_created')
    except Wallet.DoesNotExist:
        # If the user doesn't have a wallet, set wallet and transactions to None
        wallet = None
        transactions = None

    context = {
        "wallet": wallet,
        "transactions": transactions
    }

    return render(request, "user_panel/wallet.html", context)


@csrf_exempt
@check_blocked
def add_cash(request):
    if request.method == "POST":
        email = request.session.get('email')
        user = Customers.objects.get(email=email)
        
        # Get the amount from the POST request
        amount_str = request.POST.get('amount')
        
        # Remove the comma from the amount string and convert it to a Decimal
        amount = Decimal(amount_str.replace(',', ''))
        
        # Create a Razorpay client with your Razorpay API key and secret
        client = razorpay.Client(auth=("rzp_test_Os7R5CUHs9KARd", "dMgNLCLxwet33mAI6ok4uiQL"))
        
        # Create a Razorpay order for the given amount
        cash = client.order.create({
            "amount": int(amount * 100),  # Convert amount to paise
            "currency": "INR", 
            "payment_capture": '1'  # Auto capture payment
        })

        context = {
            "payment_details": {
                "id": cash['id'], 
                "amount": str(amount),  # Convert Decimal to string
                "currency": "INR",
                "key": "rzp_test_Os7R5CUHs9KARd",
                "name": user.first_name, 
                "email": email 
            } 
        }

        # Return the Razorpay add cash template with the payment details
        return render(request, "user_panel/razorpay_add_cash.html", context)
    
    else:
        # If the request method is not POST, render the wallet template
        # Fetch the wallet and transaction history for the user
        email = request.session.get('email')
        user = Customers.objects.get(email=email)
        
        try:
            # Retrieve the user's wallet
            wallet = Wallet.objects.get(user=user)
            
            # Retrieve the user's transaction history
            transactions = Transaction.objects.filter(wallet=wallet).order_by('-date_created')
        except Wallet.DoesNotExist:
            # If the user doesn't have a wallet, set wallet and transactions to None
            wallet = None
            transactions = None

        context = {
            "wallet": wallet,
            "transactions": transactions
        }
        
        return render(request, "user_panel/wallet.html", context)

 # Return an HttpResponse object for GET requests


@csrf_exempt
def handle_razorpay_success(request):
    if request.method == "POST":
        # Extract payment information from the POST request
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        email = request.POST.get('email')
        amount = Decimal(request.POST.get('amount'))  # Convert amount to Decimal
        
        # Retrieve the user object
        user = Customers.objects.get(email=email)
        
        # Retrieve or create the user's wallet object
        wallet, created = Wallet.objects.get_or_create(user=user)
        
        # Update the wallet balance
        wallet.balance += amount
        wallet.save()

        # Save the transaction
        transaction = Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type='Credit'  # Assuming it's a credit transaction
        )

        # Pass context data to the success template
        context = {
            "total_amount": amount,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_order_id": razorpay_order_id,
            "wallet_balance": wallet.balance,
            "email": email  
        }

        # Render the success template with context data
        return render(request, 'user_panel/cash_add_success.html', context)
    else:
        # Handle cases where the request method is not POST (optional)
        return render(request, 'user_panel/wallet.html')




def handle_razorpay_failure(request):
    # Add your logic for handling failed payments
    messages.error(request, 'Payment failed. Please try again.')
    return redirect('user_panel:wallet.html')

