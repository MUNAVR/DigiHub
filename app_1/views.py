from django.shortcuts import render,redirect
from django.contrib.auth.models import User,Group
from.models import *
from django.contrib import messages
# from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
import random
from products.models import Product_Variant,Attribute_Value
from django.contrib.auth.hashers import check_password
from django.core import serializers
from django.http import JsonResponse
from django.template.loader import render_to_string
import re
from django.shortcuts import render, redirect
from .models import Customers
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from app_1.decorators import check_blocked
from django.contrib.auth.decorators import login_required
from category.models import Brand


def google_oauth_callback(request):
    return redirect("user:index")

def signup(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        contact = request.POST.get('mobile')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')


        # Validate first name format
        if not validate_name(fname):
            messages.error(request, 'name starts with a capital letter and contains only letters')
            return redirect('user:signup')

        # Validate last name format
        if not validate_name(lname):
            messages.error(request, 'Invalid last name format.')
            return redirect('user:signup')

        # Check if email is already registered
        if Customers.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return redirect('user:signup')

        try:
            # Validate email format
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email format.')
            return redirect('user:signup')
        
        # Validate contact number
        if not validate_contact(contact):
            messages.error(request, 'Invalid contact number format.')
            return redirect('user:signup')
        
        # Check if passwords match
        if pass1 != pass2:
            messages.error(request, 'Passwords do not match.')
            return redirect('user:signup')

        
        # Validate password format
        if not validate_password(pass1):
            messages.error(request, 'Password must be at least 6 characters long, including one number, and no spaces.')
            return redirect('user:signup')
        
        # Save user details in session
        request.session['fname'] = fname
        request.session['lname'] = lname
        request.session['email'] = email
        request.session['contact'] = contact
        request.session['password'] = pass1

        random_num = random.randint(1000, 9999)
        request.session['OTP_Key'] = random_num
        send_mail(
            "OTP AUTHENTICATING DIGIHUB",
            f"{random_num} -OTP",
            "munavarmjp@gmail.com",
            [email],
            fail_silently=False,
        )
        return redirect('user:verify_otp')
    else:
        return render(request, "user_panel/signup.html")

def validate_email(email):
    from django.core.validators import validate_email as django_validate_email
    from django.core.exceptions import ValidationError
    try:
        django_validate_email(email)
        domain = email.split('@')[1]  # Get the domain part of the email
        if domain == 'gmail.com':  # Check if the domain is gmail.com
            return True
        else:
            return False
    except ValidationError:
        return False


def validate_name(name):
    # Check if name starts with a capital letter and contains only letters
    return bool(re.match(r'^[A-Z][a-z]*$', name))

def validate_contact(contact):
    # Check if contact is numeric, not all zeros, and has a length of 10
    return bool(re.match(r'^[1-9][0-9]{9}$', contact))

def validate_password(password):
    # Check if password is at least 6 characters long, includes one number, and has no spaces
    return bool(re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', password))


def verify_otp(request):
    if request.method == "POST":
        if str(request.session.get('OTP_Key')) != str(request.POST.get('otp')):
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('user:verify_otp')
        else:
            # OTP verification successful, save user details
            fname = request.session.get('fname')
            lname = request.session.get('lname')
            email = request.session.get('email')
            contact = request.session.get('contact')
            password = request.session.get('password')
            user = Customers(first_name=fname, last_name=lname, email=email, phone=contact, password=password)
            user.save()
            
            # Clear session data after successful registration
            del request.session['OTP_Key']
            del request.session['fname']
            del request.session['lname']
            del request.session['email']
            del request.session['contact']
            del request.session['password']

            messages.success(request, "Registration successful! Please login.")
            return redirect('user:login')

    return render(request, 'user_panel/email_otp.html')


def resend_otp(request):
    if 'OTP_Key' in request.session:
        del request.session['OTP_Key']

    random_num = random.randint(1000, 9999)
    request.session['OTP_Key'] = random_num
    send_mail(
        "OTP AUTHENTICATING DIGIHUB",
        f"Your OTP is: {random_num}",
        "munavarmjp@gmail.com",
        [request.session.get('email')],
        fail_silently=False,
    )

    messages.success(request, "OTP has been resent successfully!")

    # Redirect to the 'verify-otp' URL
    return redirect('user:verify_otp')


def login(request):
    error_message = None  # Initialize error message

    if 'email' in request.session:
        # Redirect if the user is already logged in
        return redirect('user:index')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass')  # Change variable name from password1 to password

        if not email or not password:  # Check if email and password are provided
            error_message = 'Email and password are required.'
        else:
            try:
                customer = Customers.objects.get(email=email)
                if customer.is_blocked:
                    error_message = 'Your account is blocked.'
                else:
                    if password == customer.password:
                        # Password comparison using Django's check_password function
                        request.session['email'] = email
                        return redirect('user:index')   
                    else:
                        error_message = 'Incorrect email or password.'
            except Customers.DoesNotExist:
                error_message = 'No account found with this email.'

    context = {
        'error_message': error_message
    }
    return render(request, 'user_panel/login.html', context)


def forgot_pass(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        number = request.POST.get('number')
        password1 = request.POST.get('new_pass1')
        password2 = request.POST.get('new_pass2')
        
        try:
            user = Customers.objects.get(email=email)
            
            # Check if contact number matches the one stored in the database
            if str(user.phone).strip() != str(number).strip():
                messages.error(request, "Contact number does not match")
                return redirect('user:forgot_pass')

            
            # Validate contact number
            if not validate_contact(number):
                messages.error(request, 'Invalid contact number format.')
                return redirect('user:forgot_pass')
            
            # Validate password
            if password1 != password2:
                messages.error(request, "New passwords do not match")
                return redirect('user:forgot_pass')
            elif not validate_password(password1):
                messages.error(request, 'Password must be at least 6 characters long, including one number, and no spaces.')
                return redirect('user:forgot_pass')
            
            # Save the new password and redirect to login
            user.password=password1
            user.save()
            messages.success(request, "Password changed successfully. Please log in with your new password.")
            return redirect('user:login')
        
        except Customers.DoesNotExist:
            messages.error(request, "User does not exist")
            return redirect('user:forgot_pass')
    
    return render(request, "user_panel/forgot_panel.html")



def logout(request):
    if 'email' in request.session:
        request.session.flush()
    return redirect('user:login')


def index(request):
    # Get all active product variants with their related products, categories, brands, and attributes
    variants = Product_Variant.objects.filter(
        product__is_active=True,
        product__product_category__is_active=True,
        product__product_brand__is_active=True,
    ).select_related('product', 'product__product_category', 'product__product_brand')

    # Filter variants further to include only those with all active attributes
    active_variants = []
    for variant in variants:
        if all(attribute.is_active for attribute in variant.attributes.all()):
            active_variants.append(variant)

    # Order the active variants by sale price
    active_variants = sorted(active_variants, key=lambda x: x.sale_price, reverse=True)

    # Get the latest 4 active variants
    new_variants = active_variants[:4]

    context = {
        "variant": active_variants,
        "new_variant": new_variants,
        "count": len(active_variants)
    }

    return render(request, "user_panel/index.html", context)






def sort_products(request):
    sort_by = request.GET.get('sort_by')

    # Handle invalid sort_by values
    if sort_by not in ['low_to_high', 'high_to_low', 'a_to_z', 'z_to_a']:
        return JsonResponse({'error': 'Invalid sort_by value'})
    
    new_variant=Product_Variant.objects.all().order_by('-created_at')[:4] 

    # Query the database based on sort_by value
    if sort_by == 'low_to_high':
        variants = Product_Variant.objects.all().order_by('sale_price')
    elif sort_by == 'high_to_low':
        variants = Product_Variant.objects.all().order_by('-sale_price')
    elif sort_by == 'a_to_z':
        variants = Product_Variant.objects.all().order_by('product__product_name')
    else: 
        sort_by == 'z_to_a'
        variants = Product_Variant.objects.all().order_by('-product__product_name')

    # Render the template with the sorted variants
    html = render_to_string("user_panel/index.html", {'variant': variants,'new_variant':new_variant})
    return JsonResponse({'html': html})





@check_blocked
def product_details(request, id):
    if 'email' not in request.session:
        return redirect('user:login')

    # Check if the user is blocked
    user = Customers.objects.get(email=request.session['email'])
    if user.is_blocked:
        messages.error(request, "You are blocked. Please contact support for assistance.")
        return redirect('user:login')  # Replace 'blocked_page' with the appropriate URL name or path
    
    # Filter active brands
    brands = Brand.objects.filter(is_active=True)
    
    # Retrieve product variant and pass it to the template context
    product_variant = Product_Variant.objects.filter(pk=id) 
    context = {
        "variant": product_variant,
        "brands": brands,  # Corrected variable name
       
    }
    return render(request, "user_panel/product_details.html", context)






# user side-------------------------------------------------------------------


@check_blocked
def user_profile(request):
    if 'email' not in request.session:
        return redirect('user:login')

    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        new_email = request.POST['email']
        contact = request.POST['mobile']

        if not validate_name(fname):
            error_message = 'Name should start with a capital letter and contain only letters.'
            messages.error(request, error_message)
            return redirect('user:user_profile')

        if not validate_name(lname):
            error_message = 'Invalid last name format.'
            messages.error(request, error_message)
            return redirect('user:user_profile')

        if not validate_contact(contact):
            error_message = 'Invalid contact number format.'
            messages.error(request, error_message)
            return redirect('user:user_profile')

        try:
            validate_email(new_email)
        except ValidationError:
            error_message = 'Invalid email format.'
            messages.error(request, error_message)
            return redirect('user:user_profile')


        try:
            current_email = request.session['email']
            user = Customers.objects.get(email=current_email)
            user.first_name = fname
            user.last_name = lname
            user.email = new_email
            user.phone = contact
            user.save()

            # Update session with new email
            request.session['email'] = new_email

            return redirect('user:user_profile')
        except Customers.DoesNotExist:
            return redirect('user:login')

    # If it's a GET request, display the user profile form
    try:
        email = request.session['email']
        user = Customers.objects.get(email=email)
        context = {
            'user': user,
        }
        return render(request, "user_panel/user_profile.html", context)
    except Customers.DoesNotExist:
        return redirect('user:login')


@check_blocked
def add_address1(request):
    if 'email' not in request.session:
        return redirect('user:login')

    current_email = request.session['email']
    user = Customers.objects.get(email=current_email)

    # Check if the user already has an address
    try:
        address1 = Address1.objects.get(user=user)
        has_address = True
    except Address1.DoesNotExist:
        address1 = None
        has_address = False

    error_message = None

    if request.method == 'POST':
        locality = request.POST.get('locality')
        pincode = request.POST.get('pin')
        district = request.POST.get('district')
        state = request.POST.get('state')
        address_text = request.POST.get('address')

        if not validate_locality(locality):
            error_message = 'Locality should start with a capital letter and contain only letters.'

        elif not validate_pincode(pincode):
            error_message = 'Invalid pincode format.'

        elif not validate_district(district):
            error_message = 'District should start with a capital letter and contain only letters.'

        elif not validate_state(state):
            error_message = 'State should start with a capital letter and contain only letters.'

        elif not validate_address(address_text):
            error_message = 'Address should contain only letters and numbers.'

        if error_message:
            # If there is an error message, display it on the form
            messages.error(request, error_message)
            context = {
                'address1': address1,
                'has_address': has_address,
                'error_message': error_message
            }
            return render(request, 'user_panel/address1.html', context)

        if has_address:
            # If the user already has an address, update it
            address1.address = address_text
            address1.locality = locality
            address1.pincode = pincode
            address1.district = district
            address1.state = state
            address1.save()
            messages.success(request, 'Address one is updated.')
        else:
            # If the user doesn't have an address, create a new one
            Address1.objects.create(
                user=user,
                address=address_text,
                locality=locality,
                pincode=pincode,
                district=district,
                state=state
            )
            messages.success(request, 'Address one is created.')

        return redirect('user:user_profile')

    context = {
        'address1': address1,
        'has_address': has_address
    }
    return render(request, 'user_panel/address1.html', context)



def validate_locality(locality):
    # Check if locality starts with a capital letter and contains only letters
    return locality[0].isupper() and locality.isalpha()

def validate_pincode(pincode):
    # Check if pincode contains only digits and has a length of 6
    return pincode.isdigit() and len(pincode) == 6

def validate_district(district):
    # Check if district starts with a capital letter and contains only letters
    return district[0].isupper() and district.isalpha()

def validate_state(state):
    # Check if state starts with a capital letter and contains only letters
    return state[0].isupper() and state.isalpha()

def validate_address(address):
    # Check if address contains only letters and numbers
    return bool(re.match('^[a-zA-Z0-9\s]+$', address.strip()))


@check_blocked
def delete_address(request):
    if 'email' not in request.session:
        return redirect('user:login')

    if request.method == 'POST':
        current_email = request.session['email']
        user = Customers.objects.get(email=current_email)

        # Check if the user has an address
        try:
            address1 = Address1.objects.get(user=user)
            # If the user has an address, delete it
            address1.delete()

        except Address1.DoesNotExist:
            pass  # No address to delete

    return redirect('user:user_profile')




@check_blocked
def add_address2(request):
    if 'email' not in request.session:
        return redirect('user:login')

    current_email = request.session['email']
    user = Customers.objects.get(email=current_email)

    try:
        address2 = Address2.objects.get(user=user)
        has_address = True
    except Address2.DoesNotExist:
        address2 = None
        has_address = False

    error_message = None  # Define error_message here

    if request.method == 'POST':
        locality = request.POST['locality']
        pincode = request.POST['pin']
        district = request.POST['district']
        state = request.POST['state']
        address_text = request.POST['address']

        if not validate_locality(locality):
            error_message = 'Locality should start with a capital letter and contain only letters.'

        elif not validate_pincode(pincode):
            error_message = 'Invalid pincode format.'

        elif not validate_district(district):
            error_message = 'District should start with a capital letter and contain only letters.'

        elif not validate_state(state):
            error_message = 'State should start with a capital letter and contain only letters.'
            
        elif not validate_address(address_text):
            error_message = 'Address should contain only letters and numbers.'
        
        if error_message:
            # If there is an error message, display it on the form
            messages.error(request, error_message)
            context = {
                'address2': address2,
                'has_address': has_address,
                'error_message': error_message
            }
            return render(request, 'user_panel/address2.html', context)

        if has_address:
            address2.address = address_text
            address2.locality = locality
            address2.pincode = pincode
            address2.district = district
            address2.state = state
            address2.save()
            messages.success(request, 'Address two is updated.')
        else:
            Address2.objects.create(
                user=user,
                address=address_text,
                locality=locality,
                pincode=pincode,
                district=district,
                state=state
            )
            messages.success(request, 'Address one is Created.')

        return redirect('user:user_profile')

    context = {
        'address2': address2,
        'has_address': has_address
    }
    return render(request, "user_panel/address2.html", context)
  # Added missing context



@check_blocked
def delete_address2(request):

    if 'email' not in request.session:
        return redirect('user:login')

    if request.method == 'POST':
        current_email = request.session['email']
        user = Customers.objects.get(email=current_email)

        # Check if the user has an address
        try:
            address2 = Address2.objects.get(user=user)
            # If the user has an address, delete it
            address2.delete()

        except Address2.DoesNotExist:
            pass  # No address to delete

    return redirect('user:user_profile')




@check_blocked
def change_pass(request):

    if request.method == 'POST':
        old_pass = request.POST['old_pass']
        new_pass1 = request.POST['new_pass1']
        new_pass2 = request.POST['new_pass2']

        current_email = request.session.get('email')
        if not current_email:
            return redirect('user:login')

        user = Customers.objects.get(email=current_email)

        # Retrieve the user's password from the database
        user_password = user.password

        # Check if the old password matches the password in the database
        if old_pass != user_password:
            messages.error(request, 'Incorrect old password')
            return redirect('user:change_pass')
        
        elif not validate_password(new_pass1):
                messages.error(request, 'Password must be at least 6 characters long, including one number, and no spaces.')
                return redirect('user:forgot_pass')
        
        print("evide ethiyo")
        # Check if the new passwords match
        if new_pass1 != new_pass2:
            messages.error(request, 'New passwords do not match')
            return redirect('user:change_pass')

        # Update the user's password
        user.password=new_pass1
        user.save()

        messages.success(request, 'Password changed successfully')
        return redirect('user:user_profile')
    else:
        return render(request, "user_panel/change_password.html")




