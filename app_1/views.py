from django.shortcuts import render,redirect
from django.contrib.auth.models import User,Group
from.models import *
from django.contrib import messages
# from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
import random
from products.models import Product_Variant
from django.contrib.auth.hashers import check_password



def google_oauth_callback(request):
    return redirect("user:index")
def signup(request):
    if request.method =='POST':
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        contact=request.POST['mobile']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']

        if pass1 != pass2:
            return  redirect('signup',{'error':'Password does not match.'})
        elif Customers.objects.filter(email=email).exists():
            return redirect('signup',{'error':'Email is already registered.'})
        else:
            users=Customers(first_name=fname,last_name=lname,email=email,phone=contact,password=pass1)
            users.save()
            return redirect('user:login')
    else:
        return render(request,"user_panel/signup.html")

def sent_otp(request):
    random_num = random.randint(1000, 9999)
    if request.method == 'POST':
        email=request.POST['email']
        request.session['OTP_Key'] = random_num
        send_mail(
            "OTP AUTHENTICATING DIGIHUB",
            f"{random_num} -OTP",
            "munavarmjp@gmail.com",
            [email],
            fail_silently=False,
        )
        return redirect('user:verify_otp')

    return render(request,"user_panel/email_send.html")

def verify_otp(request):
   if request.method=="POST":
      if str(request.session['OTP_Key']) != str(request.POST['otp']):
         print(request.session['OTP_Key'],request.POST['otp'])
      else:
         messages.success(request, "signup successful!")
         return redirect('user:signup')
   return render(request,'user_panel/email_otp.html')


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
    if 'email' in request.session:
        return redirect('user:index')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass')

        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return render(request, 'user_panel/login.html')

        try:
            customer = Customers.objects.get(email=email, is_blocked=False)
            if password == customer.password:  # Directly compare passwords if stored in plain text
                request.session['email'] = email
                return redirect('user:index')
            else:
                messages.error(request, 'Incorrect email or password')
        except Customers.DoesNotExist:
            messages.error(request, 'No account found with this email')
        except Customers.MultipleObjectsReturned:
            messages.error(request, 'Multiple accounts found with this email. Please contact support.')

    return render(request, 'user_panel/login.html')



def forgot_pass(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        number = request.POST.get('number')
        password1 = request.POST.get('new_pass1')
        password2 = request.POST.get('new_pass2')
        
        try:
            user = Customers.objects.get(email=email)
            contact = user.phone
            print(number,contact)
            if contact == number:
                messages.error(request, "Number does not match")
                return redirect('user:forgot_pass')
            
            if password1 != password2:
                messages.error(request, "New passwords do not match")
                return redirect('user:forgot_pass')
            else:
                user.password=password1
                user.save()
                messages.success(request, "Password changed successfully")
                return redirect('user:login')
        except Customers.DoesNotExist:
            messages.error(request, "User does not exist")
            return redirect('user:forgot_pass')
    
    return render(request, "user_panel/forgot_panel.html")


def logout(request):
    if 'email' in request.session:
        request.session.flush()
    return redirect('user:login')

from django.http import JsonResponse
from django.template.loader import render_to_string

def index(request):
    variant=Product_Variant.objects.all()
    context={
        "variant":variant
    }
    return render(request,"user_panel/index.html",context)



# @login_required(login_url='login')
def product_details(request,id):
    if 'email' not in request.session:
        return redirect('user:login')
    product_variant=Product_Variant.objects.filter(pk=id)
    context={
        "variant":product_variant
    }
    return render(request,"user_panel/product_details.html",context)



# user side-------------------------------------------------------------------

def user_profile(request):
    if 'email' not in request.session:
        return redirect('user:login')

    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        new_email = request.POST['email']
        contact = request.POST['mobile']

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
            # Handle the case where user does not exist
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
        # Handle the case where user does not exist
        return redirect('user:login')

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

    if request.method == 'POST':
        locality = request.POST['locality']
        pincode = request.POST['pin']
        district = request.POST['district']
        state = request.POST['state']
        address_text = request.POST['address']

        if has_address:
            # If the user already has an address, update it
            address1.address = address_text
            address1.locality = locality
            address1.pincode = pincode
            address1.district = district
            address1.state = state
            address1.save()
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

        return redirect('user:user_profile')

    context = {
        'address1': address1,
        'has_address': has_address
    }
    return render(request, 'user_panel/address1.html',context)


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


def add_address2(request):
    if 'email' not in request.session:
        return redirect('user:login')

    current_email = request.session['email']
    user = Customers.objects.get(email=current_email)

    try:
        address2 = Address2.objects.get(user=user)
        has_address = True
    except Address2.DoesNotExist:  # Corrected to Address2.DoesNotExist
        address2 = None
        has_address = False

    if request.method == 'POST':
        locality = request.POST['locality']
        pincode = request.POST['pin']
        district = request.POST['district']
        state = request.POST['state']
        address_text = request.POST['address']

        if has_address:
            address2.address = address_text
            address2.locality = locality
            address2.pincode = pincode
            address2.district = district
            address2.state = state
            address2.save()
        else:
            Address2.objects.create(
                user=user,
                address=address_text,
                locality=locality,
                pincode=pincode,
                district=district,
                state=state
            )

        return redirect('user:user_profile')

    context = {
        'address2': address2,
        'has_address': has_address
    }
    return render(request, "user_panel/address2.html", context)  # Added missing context


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


from django.contrib.auth.hashers import check_password

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




