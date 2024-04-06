from django.shortcuts import render,redirect
from django.contrib.auth.models import User,Group
from.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
import random
from products.models import Product_Variant,Attribute_Value
from django.contrib.auth.hashers import check_password
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
from django.db.models import F, Max, Min
from datetime import date
from offers.models import ReferralOffer
from django.db import transaction
from wallet.models import Wallet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_control
from .helpers import send_forget_password_mail


def signup(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        contact = request.POST.get('mobile')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        referred_by=request.POST.get('referred_by')


        
        if not validate_name(fname):
            messages.error(request, 'name starts with a capital letter and contains only letters')
            return redirect('user:signup')

        
        if not validate_name(lname):
            messages.error(request, 'Invalid last name format.')
            return redirect('user:signup')

        
        if Customers.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return redirect('user:signup')

        try:
           
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email format.')
            return redirect('user:signup')
        
        
        if not validate_contact(contact):
            messages.error(request, 'Invalid contact number format.')
            return redirect('user:signup')
        
        
        if pass1 != pass2:
            messages.error(request, 'Passwords do not match.')
            return redirect('user:signup')
        
        
        if validate_referred(referred_by):
            messages.error(request, 'Referred ID can only contain letters and digits, and must not be all the same character.')
            return redirect('user:signup')
        
       
        if not validate_password(pass1):
            messages.error(request, 'Password must be at least 6 characters long, including one number, and no spaces.')
            return redirect('user:signup')
        
       
        request.session['fname'] = fname
        request.session['lname'] = lname
        request.session['email'] = email
        request.session['contact'] = contact
        request.session['password'] = pass1
        request.session['referred_by']=referred_by

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
        domain = email.split('@')[1]  
        if domain == 'gmail.com': 
            return True
        else:
            return False
    except ValidationError:
        return False


def validate_name(name):
    return bool(re.match(r'^[A-Z][a-z]*$', name))

def validate_contact(contact):
    return bool(re.match(r'^[1-9][0-9]{9}$', contact))

def validate_password(password):
    return bool(re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', password))

def validate_referred(referred):
    if not re.match(r'^[a-zA-Z0-9]+$', referred) or len(set(referred)) == 1:
        return False
    return True

def verify_otp(request):
    if request.method == "POST":
        if str(request.session.get('OTP_Key')) != str(request.POST.get('otp')):
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('user:verify_otp')
        else:
            
            fname = request.session.get('fname')
            lname = request.session.get('lname')
            email = request.session.get('email')
            contact = request.session.get('contact')
            password = request.session.get('password')
            referred_by=request.session.get('referred_by')

            with transaction.atomic():
                user= Customers(first_name=fname, last_name=lname, email=email, phone=contact, password=password)
                user.save()

                wallet, created = Wallet.objects.get_or_create(user=user)

                # If the user was referred, add referral amount to the wallet
                if referred_by:
                    referred_offer = ReferralOffer.objects.get(referral_code=referred_by)
                    referred_amount = referred_offer.referral_amount
                    wallet.balance += referred_amount
                    wallet.save()
                

            # Clear session data after successful registration
            del request.session['OTP_Key']
            del request.session['fname']
            del request.session['lname']
            del request.session['email']
            del request.session['contact']
            del request.session['password']
            del request.session['referred_by']
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
    return redirect('user:verify_otp')




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
    error_message = None 

    if 'email' in request.session:
        return redirect('user:index')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass') 

        if not email or not password: 
            error_message = 'Email and password are required.'
        else:
            try:
                customer = Customers.objects.get(email=email)
                if customer.is_blocked:
                    error_message = 'Your account is blocked.'
                else:
                    if password == customer.password:
                        # Password comparison using Django's check_password function
                        request.session['is_logged_in'] = True
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




# def forgot_pass(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         number = request.POST.get('number')
#         password1 = request.POST.get('new_pass1')
#         password2 = request.POST.get('new_pass2')
        
#         try:
#             user = Customers.objects.get(email=email)
            
#             # Check if contact number matches the one stored in the database
#             if str(user.phone).strip() != str(number).strip():
#                 messages.error(request, "Contact number does not match")
#                 return redirect('user:forgot_pass')

            
           
#             if not validate_contact(number):
#                 messages.error(request, 'Invalid contact number format.')
#                 return redirect('user:forgot_pass')
            
            
#             if password1 != password2:
#                 messages.error(request, "New passwords do not match")
#                 return redirect('user:forgot_pass')
#             elif not validate_password(password1):
#                 messages.error(request, 'Password must be at least 6 characters long, including one number, and no spaces.')
#                 return redirect('user:forgot_pass')
            
            
#             user.password=password1
#             user.save()
#             messages.success(request, "Password changed successfully. Please log in with your new password.")
#             return redirect('user:login')
        
#         except Customers.DoesNotExist:
#             messages.error(request, "User does not exist")
#             return redirect('user:forgot_pass')
    
#     return render(request, "user_panel/forgot_panel.html")


def logout(request):
    if 'email' in request.session:
        request.session.flush()
    return redirect('user:login')


import uuid
def ForgetPassword(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            
            if not Customers.objects.filter(email=email).first():
                messages.success(request, 'Not user found with this email.')
                return redirect('user:forget_password')
            
            user_obj = Customers.objects.get(email = email)
            token = str(uuid.uuid4())
            send_forget_password_mail(email)
            messages.success(request, 'email is sent.')
            return redirect('user:forget_password')
            
    except Exception as e:
        print(e)
    return render(request , "user_panel/forgot_panel.html")


def ChangePassword(request):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('reconfirm_password')
            first_name= request.POST.get('first_name')
            
            name=Customers.objects.get(first_name=first_name)
            if name is  None:
                messages.success(request, 'No user id found.')
                return redirect('user:change-password')
                
            
            if  new_password != confirm_password:
                messages.success(request, 'both should  be equal.')
                return redirect('user:change-password')
                         
            
            user_obj =Customers.objects.get(first_name=first_name)
            user_obj.password=new_password
            user_obj.save()
            messages.success(request,'Password changed successfully. Please log in with your new password.')
            return redirect('user:login')
        
        return render(request ,'user_panel/change-password.html')





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):

    variants = Product_Variant.objects.filter(
        product__is_active=True,
        product__product_category__is_active=True,
        product__product_brand__is_active=True,
        is_active=True
    ).select_related('product', 'product__product_category', 'product__product_brand')

    
    active_variants = [variant for variant in variants if all(attribute.is_active for attribute in variant.attributes.all())]

    
    active_variants = sorted(active_variants, key=lambda x: x.sale_price, reverse=True)
    brands = Brand.objects.filter(is_active=True)
   
    paginator = Paginator(active_variants, 5) 
    page_number = request.GET.get('page')

    try:
        active_variants = paginator.page(page_number)
    except PageNotAnInteger:
       
        active_variants = paginator.page(1)
    except EmptyPage:
        
        active_variants = paginator.page(paginator.num_pages)

    new_variant = Product_Variant.objects.all().order_by('-created_at')[:4]

    context = {
        "variant": active_variants,
        "new_variant": new_variant,
        "count": paginator.count,
        "brands": brands,
    }

    return render(request, "user_panel/index.html", context)




def sort_products(request):
    sort_by = request.GET.get('sort_by')

   
    if sort_by not in ['low_to_high', 'high_to_low', 'a_to_z', 'z_to_a']:
        return JsonResponse({'error': 'Invalid sort_by value'})
    
    new_variant=Product_Variant.objects.all().order_by('-created_at')[:4] 

   
    if sort_by == 'low_to_high':
        variants = Product_Variant.objects.all().order_by('sale_price')
    elif sort_by == 'high_to_low':
        variants = Product_Variant.objects.all().order_by('-sale_price')
    elif sort_by == 'a_to_z':
        variants = Product_Variant.objects.all().order_by('product__product_name')
    else: 
        sort_by == 'z_to_a'
        variants = Product_Variant.objects.all().order_by('-product__product_name')

    
    html = render_to_string("user_panel/index.html", {'variant': variants,'new_variant':new_variant})
    return JsonResponse({'html': html})


@check_blocked
def product_details(request, id):
    if 'email' not in request.session:
        return redirect('user:login')

    
    user = Customers.objects.get(email=request.session['email'])
    if user.is_blocked:
        messages.error(request, "You are blocked. Please contact support for assistance.")
        return redirect('user:login')  
    
    
    brands = Brand.objects.filter(is_active=True)
        
    
    product_variant = Product_Variant.objects.get(pk=id)
    product=product_variant.product
    print(product)
    all_variant=Product_Variant.objects.filter(product=product)
   
    context = {
        "all_variant":all_variant,  
        "variant": product_variant,
        "brands": brands,
    }
    return render(request, "user_panel/product_details.html", context)



def get_product_details(request):
    print("here")
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        variant_id = request.GET.get('variant_id')
        print(variant_id)
        if variant_id:
            brands = Brand.objects.filter(is_active=True)
            product_variant = get_object_or_404(Product_Variant, pk=variant_id)
            product=product_variant.product
            all_variant=Product_Variant.objects.filter(product=product)
            context = {
                "all_variant":all_variant,  
                "variant": product_variant,
                "brands": brands,
            }
            product_details_html = render_to_string('user_panel/product_details.html',context)
            return JsonResponse({'product_details_html': product_details_html})
        else:
            return JsonResponse({'error': 'Variant ID not provided'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)





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

            
            request.session['email'] = new_email

            return redirect('user:user_profile')
        except Customers.DoesNotExist:
            return redirect('user:login')

    
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
            
            messages.error(request, error_message)
            context = {
                'address1': address1,
                'has_address': has_address,
                'error_message': error_message
            }
            return render(request, 'user_panel/address1.html', context)

        if has_address:
            
            address1.address = address_text
            address1.locality = locality
            address1.pincode = pincode
            address1.district = district
            address1.state = state
            address1.save()
            messages.success(request, 'Address one is updated.')
        else:
            
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
    return locality[0].isupper() and locality.isalpha()

def validate_pincode(pincode):
    return pincode.isdigit() and len(pincode) == 6

def validate_district(district):
    return district[0].isupper() and district.isalpha()

def validate_state(state):
    return state[0].isupper() and state.isalpha()

def validate_address(address):
    return bool(re.match('^[a-zA-Z0-9\s]+$', address.strip()))


@check_blocked
def delete_address(request):
    if 'email' not in request.session:
        return redirect('user:login')

    if request.method == 'POST':
        current_email = request.session['email']
        user = Customers.objects.get(email=current_email)

        
        try:
            address1 = Address1.objects.get(user=user)

            address1.delete()

        except Address1.DoesNotExist:
            pass

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

    error_message = None 

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
  



@check_blocked
def delete_address2(request):

    if 'email' not in request.session:
        return redirect('user:login')

    if request.method == 'POST':
        current_email = request.session['email']
        user = Customers.objects.get(email=current_email)

        
        try:
            address2 = Address2.objects.get(user=user)
            
            address2.delete()

        except Address2.DoesNotExist:
            pass 

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

        
        user_password = user.password

       
        if old_pass != user_password:
            messages.error(request, 'Incorrect old password')
            return redirect('user:change_pass')
        
        elif not validate_password(new_pass1):
                messages.error(request, 'Password must be at least 6 characters long, including one number, and no spaces.')
                return redirect('user:forgot_pass')
        
        print("evide ethiyo")
       
        if new_pass1 != new_pass2:
            messages.error(request, 'New passwords do not match')
            return redirect('user:change_pass')

       
        user.password=new_pass1
        user.save()

        messages.success(request, 'Password changed successfully')
        return redirect('user:user_profile')
    else:
        return render(request, "user_panel/change_password.html")




