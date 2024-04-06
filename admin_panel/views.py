from django.shortcuts import render,redirect
from app_1.models import *
from django.contrib import messages,auth
from checkout.models import Order
from django.urls import reverse
from django.http import JsonResponse
from products.models import Product_Variant,Products
from datetime import datetime, timedelta,time
from django.db.models import Sum
from datetime import datetime
from django.http import HttpResponse
from django.db.models import Sum
from django.template.loader import get_template
from django.views import View
from io import BytesIO
from xhtml2pdf import pisa
from datetime import date
from django.utils import timezone
import xlsxwriter
from io import BytesIO
from coupon.models import Coupon,CouponUsage
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from checkout.models import OrderProduct
from products.models import Product_Variant,Products
from wallet.models import Wallet,Transaction



# Create your views here.

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_index(request):
    if 'username' not in request.session:
        return redirect('admin_login')
    total_order = Order.objects.count()
    total_product = Products.objects.count()
    total_product_variant = Product_Variant.objects.count()
    total_completed=Order.objects.filter(order_status="Completed").count()
    total_cancelled=Order.objects.filter(order_status="Cancelled").count()
    total_Pending=Order.objects.filter(order_status="Pending").count()
    total_Shipped=Order.objects.filter(order_status="Shipped").count()
    
    total_earnings = calculate_total_earnings()

    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    monthly_earnings = calculate_monthly_earnings(current_year, current_month)

    current_year = datetime.now().year
    yearly_earnings = calculate_yearly_earnings(current_year)

    context = {
        'total_order': total_order,
        'total_product': total_product,
        'total_product_variant': total_product_variant,
        'total_earnings': total_earnings,
        'monthly_earnings': monthly_earnings,
        'yearly_earnings': yearly_earnings,
        'total_completed':total_completed,
        'total_cancelled':total_cancelled,
        'total_Pending':total_Pending,
        'total_Shipped':total_Shipped,

    }
    return render(request, "admin_panel/admin_index.html", context)



def calculate_monthly_earnings(year, month):
    
    start_date = datetime(year, month, 1)
    end_date = start_date.replace(month=month % 12 + 1, day=1) if month < 12 else start_date.replace(year=year + 1, month=1)

   
    monthly_orders = Order.objects.filter(
        order_status='Completed',
        order_date__gte=start_date,
        order_date__lt=end_date
    )

    
    monthly_earnings = monthly_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    return monthly_earnings

def calculate_yearly_earnings(year):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)

    yearly_orders = Order.objects.filter(
        order_status='Completed',
        order_date__gte=start_date,
        order_date__lte=end_date
    )

    yearly_earnings = yearly_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    return yearly_earnings


def calculate_total_earnings():
   
    completed_orders = Order.objects.filter(order_status='Completed')

    
    total_earnings = completed_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    return total_earnings


def get_monthly_sales(request):
    current_date = datetime.now()
    monthly_sales = []

    for month in range(1, 13):
        start_date = datetime(current_date.year, month, 1)
        end_date = start_date.replace(month=month % 12 + 1, day=1) if month < 12 else start_date.replace(year=current_date.year + 1, month=1)

        monthly_orders = Order.objects.filter(
            order_status='Completed',
            order_date__gte=start_date,
            order_date__lt=end_date
        )

        monthly_earnings = monthly_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        monthly_sales.append(monthly_earnings)

    return JsonResponse({'monthly_sales': monthly_sales})

def get_yearly_sales(request):
    current_date = datetime.now()
    yearly_sales = []

    for year in range(current_date.year - 2, current_date.year + 1):  # Fetch data for the current year and the previous two years
        start_date = datetime(year, 1, 1)
        end_date = start_date.replace(year=year + 1, month=1)

        yearly_orders = Order.objects.filter(
            order_status='Completed',
            order_date__gte=start_date,
            order_date__lt=end_date
        )

        yearly_earnings = yearly_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        yearly_sales.append(yearly_earnings)

    return JsonResponse({'yearly_sales': yearly_sales})



class SalesReportView(View):
    def generate_report(self, start_date, end_date):
        # For daily report
        if start_date == end_date:
            start_of_day = datetime.combine(start_date.date(), time.min)  
            end_of_day = datetime.combine(start_date.date(), time.max)  

            daily_orders = Order.objects.filter(order_date__range=(start_of_day, end_of_day))
            daily_revenue = daily_orders.filter(order_status="Completed").aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            daily_cancelled_orders = daily_orders.filter(order_status="Cancelled").count()

            
            daily_discount_amount = (CouponUsage.objects.filter(date_used__date=start_date).aggregate(Sum('coupon__discount'))['coupon__discount__sum'] or 0) * daily_revenue / 100
            daily_discount_count = Coupon.objects.all().count()

            params = {
                "orders":daily_orders,
                'daily_orders_count': daily_orders.count(),
                'daily_revenue': daily_revenue,
                'daily_cancelled_orders': daily_cancelled_orders,
                'daily_discount_amount': daily_discount_amount,
                'daily_discount_count': daily_discount_count,
            }

        # For weekly report
        elif (end_date - start_date).days == 6:

            weekly_orders =Order.objects.filter(order_date__range=[start_date, end_date])
            completed_weekly_orders = weekly_orders.filter(order_status="Completed")
            
            weekly_revenue = completed_weekly_orders.aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0
            weekly_cancelled_orders = weekly_orders.filter(order_status="Cancelled").count()
            
        
           
            discount_sum = CouponUsage.objects.filter(date_used__date=start_date).aggregate(Sum('coupon__discount'))['coupon__discount__sum'] or 0
            weekly_discount_amount = round((discount_sum * weekly_revenue / 100), 2)

            
            weekly_discount_count = Coupon.objects.all().count()
    

            params = {
                "orders":weekly_orders,
                'weekly_orders_count': weekly_orders.count(),
                'weekly_revenue': weekly_revenue,
                'weekly_cancelled_orders': weekly_cancelled_orders,
                'weekly_discount_amount': weekly_discount_amount,
                'weekly_discount_count': weekly_discount_count
            }


        # For yearly report
        elif start_date.year == end_date.year:
            yearly_orders = Order.objects.filter(order_date__year=start_date.year)
            yearly_revenue = yearly_orders.filter(order_status="Completed").aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            yearly_cancelled_orders = yearly_orders.filter(order_status="Cancelled").count()

            yearly_discount_amount = round((CouponUsage.objects.filter(date_used__year=start_date.year).aggregate(Sum('coupon__discount'))['coupon__discount__sum'] or 0) * yearly_revenue / 100, 2)
            yearly_discount_count = Coupon.objects.all().count()

            params = {
                "orders":yearly_orders,
                'yearly_orders_count': yearly_orders.count(),
                'yearly_revenue': yearly_revenue,
                'yearly_cancelled_orders': yearly_cancelled_orders,
                'yearly_discount_amount': yearly_discount_amount,
                'yearly_discount_count': yearly_discount_count,
            }
        
        else:
            # Handle custom date range here
            custom_orders = Order.objects.filter(order_date__range=[start_date, end_date])
            custom_revenue = custom_orders.filter(order_status="Completed").aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            custom_cancelled_orders = custom_orders.filter(order_status="Cancelled").count()

            custom_discount_amount = (CouponUsage.objects.filter(date_used__range=[start_date, end_date]).aggregate(Sum('coupon__discount'))['coupon__discount__sum'] or 0) * custom_revenue / 100
            custom_discount_count = Coupon.objects.all().count()

            params = {
                "orders":custom_orders,
                'custom_orders_count': custom_orders.count(),
                'custom_revenue': custom_revenue,
                'custom_cancelled_orders': custom_cancelled_orders,
                'custom_discount_amount': custom_discount_amount,
                'custom_discount_count': custom_discount_count,
            }

        return params

    def render_to_pdf(self, context):
        template = get_template('admin_panel/sales_report.html')
        html = template.render(context)
        pdf_file = BytesIO()
        pisa.pisaDocument(BytesIO(html.encode("UTF-8")), pdf_file, encoding='UTF-8')
        return pdf_file.getvalue()

    def render_to_excel(self, context):
        output = BytesIO() 

        workbook = xlsxwriter.Workbook(output, {'remove_timezone': True})
        worksheet = workbook.add_worksheet('Sales Report')

        
        orders = context['orders'] 

        
        headers = ['Order ID', 'Order Date', 'Total Amount', 'Order Status'] 
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        
        for row, order in enumerate(orders, start=1):
            worksheet.write(row, 0, order.id)  
            worksheet.write(row, 1, order.order_date.replace(tzinfo=None)) 
            worksheet.write(row, 2, order.total_amount)  
            worksheet.write(row, 3, order.order_status)  

        workbook.close()
        output.seek(0) 
        return output.getvalue()


    def get(self, request, *args, **kwargs):
        report_type = request.GET.get('report_type', 'daily')
        report_format = request.GET.get('format', 'pdf')

        start_date = None
        end_date = None
        
        if report_type == 'daily':
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date
        elif report_type == 'weekly':
            end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = end_date - timedelta(days=6)
        elif report_type == 'yearly':
            end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = datetime(end_date.year, end_date.month, 1)
        
        # Provide default values if report_type is unexpected
        else:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date

        start_date = timezone.make_aware(start_date)
        end_date = timezone.make_aware(end_date)

        context = self.generate_report(start_date, end_date)

        if report_format == 'pdf':
            pdf_content = self.render_to_pdf(context)
            response = HttpResponse(pdf_content, content_type='application/pdf')
            filename = "sales_report.pdf"
        else:  
            excel_content = self.render_to_excel(context)
            response = HttpResponse(excel_content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            filename = "sales_report.xlsx"

        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response




def customer(request):
    if 'username' not in request.session:
        return redirect('admin_login')  
    data=Customers.objects.all()
    context={
        "datas":data
        }
    return render (request,"admin_panel/customer.html",context)

def customer_edit(request,id):
    if 'username' not in request.session:
        return redirect('admin_login')
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
    if 'username' not in request.session:
        return redirect('admin_login') 
    data=Customers.objects.get(id=id)
    data.delete()
    return redirect('customer')


def block_user(request, id):
    if 'username' not in request.session:
        return redirect('admin_login') 
    if request.method == 'POST':
        user = Customers.objects.get(id=id)
        user.is_blocked = True
        user.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

def unblock_user(request, id):
    if 'username' not in request.session:
        return redirect('admin_login') 
    if request.method == 'POST':
        user = Customers.objects.get(id=id)
        user.is_blocked = False
        user.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})



from django.core.paginator import Paginator

def order_list(request):
    if 'username' not in request.session:
        return redirect('admin_login') 
    order_list = Order.objects.all().order_by('-order_date')
    
    paginator = Paginator(order_list, 10)  

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    return render(request, "admin_panel/order_list.html", context)

def reject_orderAdmin(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        
        if order.order_status == 'Cancelled':
            messages.error(request, 'Order has already been cancelled.')
        else:
          
            order.order_status = 'Cancelled'
            order.save()
            
            
            order_products = OrderProduct.objects.filter(order=order)
            for order_product in order_products:
                product_variant = Product_Variant.objects.filter(product__product_name=order_product.product_name)
                product_variant.stock += order_product.quantity
                product_variant.save()
            
            messages.success(request, 'Order has been rejected successfully.')
            
           
            if order.payment_status == 'Paid' and order.order_status == 'Pending':
                wallet = Wallet.objects.get(user=order.user)
                wallet.balance += order.total_amount
                wallet.save()
                Transaction.objects.create(wallet=wallet, amount=order.total_amount, transaction_type='Credit')
                messages.info(request, 'Amount refunded to wallet successfully.')
            
            elif order.payment_status == 'Pending':
               
                pass
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')

    return redirect('order_list')



def change_status(request, order_id):
    if 'username' not in request.session:
        return redirect('admin_login') 

    if request.method == 'GET':
        new_status = request.GET.get('new_status')
        order = Order.objects.get(id=order_id)
        
        # Check if the payment status is failed
        if order.payment_status == "Failed":
            messages.error(request, 'Order status cannot be changed because the payment status is failed.')
            return redirect(reverse('order_list'))
        
        if order.order_status in ['Cancelled', 'Returned']:
            messages.error(request, 'Order status cannot be changed as it is already cancelled or returned.')
        else:
            valid_status_options = ['Pending', 'Shipped', 'Completed']
            
            if new_status.strip().title() in valid_status_options:
                new_status_title = new_status.strip().title()
                
                if order.order_status != new_status_title:
                    order.order_status = new_status_title
                    
                    if new_status_title == 'Completed':
                        order.delivery_date = datetime.now()
                    
                    order.save()
                    messages.success(request, 'Status changed successfully.')
                else:
                    messages.info(request, 'Order is already in the specified status.')
            else:
                messages.error(request, 'Invalid status provided.')
    
    return redirect(reverse('order_list'))

def best_selling_product(request):
    best_selling_products = OrderProduct.objects.values('product_name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:10]
    context={
        "best_selling_products":best_selling_products,
    }
    return render (request, "admin_panel/best_selling_product.html",context)


def best_selling_brand(request):
    
    best_selling_products = OrderProduct.objects.values('product_name').annotate(total_quantity_sold=Sum('quantity')).order_by('-total_quantity_sold')[:10]

   
    brand_sales = {}

    
    for product in best_selling_products:
        
        product_name = product['product_name']
        
        product_instance = Products.objects.get(product_name=product_name)
        
        brand_name = product_instance.product_brand.name
        
        brand_sales[brand_name] = brand_sales.get(brand_name, 0) + product['total_quantity_sold']

   
    sorted_brands = sorted(brand_sales.items(), key=lambda x: x[1], reverse=True)
    print(sorted_brands)
    context = {
        'top_selling_brands': sorted_brands
    }
    return render(request, "admin_panel/best_selling_brand.html", context)
    