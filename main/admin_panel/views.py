from django.shortcuts import render,redirect
# from app_1.models import Users
from app_1.models import *
from django.contrib import messages,auth

# Create your views here.
def admin_login(request):
    if 'username' in request.session:
        return redirect('admin_index')
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.username == 'admin':
            request.session['username'] = username
            return redirect('admin_index')
    return render(request,"admin_panel/login.html")

def admin_logout(request):
    if 'username' in request.session:
        request.session.flush()
    return redirect('admin_login')

def admin_index(request):
    return render(request,"admin_panel/admin_index.html")

def customer(request):
    data=Customers.objects.all()
    context={
        "datas":data
        }
    return render (request,"admin_panel/customer.html",context)

def customer_edit(request,id):
    data=Customers.objects.get(id=id)
    context={"data":data}
    if request.method =='POST':
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        contact=request.POST['mobile']
        pass1=request.POST['pass1']
        edit=Customers.objects.get(id=id)
        edit.first_name=fname
        edit.last_name=lname
        edit.email=email
        edit.phone=contact
        edit.password=pass1
        edit.save()
        return redirect('customer')
    return render(request,"admin_panel/customer_edit.html",context)

def customer_delete(request,id):
    data=Customers.objects.get(id=id)
    data.delete()
    return redirect('customer')

def block_user(request,id):
    user =Customers.objects.get(id=id)
    user.is_blocked =True
    user.save()
    return redirect('customer')

def unblock_user(request,id):
    user =Customers.objects.get(id=id)
    user.is_blocked =False
    user.save()
    return redirect('customer')