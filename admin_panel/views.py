from django.shortcuts import render,redirect
# from app_1.models import Users
from app_1.models import *
from django.contrib import messages,auth
from checkout.models import Order
from django.urls import reverse
from django.http import JsonResponse

# Create your views here.
def admin_login(request):
    if 'username' in request.session:
        return redirect('admin_index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)
        
        if user is not None and user.username == 'admin':
            request.session['username'] = username
            return redirect('admin_index')
        else:
            error_message = "Invalid username or password."
            return render(request, "admin_panel/login.html", {"error_message": error_message})
    
    return render(request, "admin_panel/login.html")

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


def block_user(request, id):
    if request.method == 'POST':
        user = Customers.objects.get(id=id)
        user.is_blocked = True
        user.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

def unblock_user(request, id):
    if request.method == 'POST':
        user = Customers.objects.get(id=id)
        user.is_blocked = False
        user.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})



def order_list(request):

    order = Order.objects.all().order_by('-order_date')
    context={
        "order":order
    }
    return render(request,"admin_panel/order_list.html",context)

def cancel_orderAdmin(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        
        # Check if the order is cancellable (add any conditions here)
        if order.order_status == 'Cancelled':
            messages.error(request, 'Order has already been cancelled.')
        elif order.order_status == 'Pending' and order.payment_status == 'Pending':
            # Update order status to 'Cancelled'
            order.order_status = 'Cancelled'
            order.save()
            messages.success(request, 'Order has been cancelled successfully.')
        else:
            messages.error(request, 'Order cannot be cancelled at this time.')
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')

    return redirect('order_list')



def change_status(request,order_id):
    if request.method == 'GET':
        new_status = request.GET.get('new_status')
        # Assuming you have a model named Order with a field named status
        order = Order.objects.get(id=order_id)
        if new_status in ['Pending', 'Shipped', 'Delivered']:  # Assuming these are the valid status options
            order.order_status = new_status
            order.save()
            # Adding success message
            messages.success(request, 'Status changed successfully.')
    # Redirecting back to the same page or any desired page after status change
    return redirect(reverse('order_list'))