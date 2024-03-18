from django.shortcuts import render,redirect
# from app_1.models import Users
from app_1.models import *
from django.contrib import messages,auth
from checkout.models import Order
from django.urls import reverse
from django.http import JsonResponse
from products.models import Product_Variant,Products
from datetime import datetime, timedelta
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
    total_order = Order.objects.count()
    total_product = Products.objects.count()
    total_product_variant = Product_Variant.objects.count()

    # Calculate total earnings
    total_earnings = calculate_total_earnings()

    # Calculate monthly earnings for the current month
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    monthly_earnings = calculate_monthly_earnings(current_year, current_month)

    context = {
        'total_order': total_order,
        'total_product': total_product,
        'total_product_variant': total_product_variant,
        'total_earnings': total_earnings,
        'monthly_earnings': monthly_earnings,
    }
    return render(request, "admin_panel/admin_index.html", context)

def calculate_monthly_earnings(year, month):
    # Get the first and last day of the specified month
    start_date = datetime(year, month, 1)
    end_date = start_date.replace(month=month % 12 + 1, day=1) if month < 12 else start_date.replace(year=year + 1, month=1)

    # Retrieve orders with payment completed within the specified month
    monthly_orders = Order.objects.filter(
        order_status='Completed',
        order_date__gte=start_date,
        order_date__lt=end_date
    )

    # Calculate total earnings for the month
    monthly_earnings = monthly_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    return monthly_earnings

def calculate_total_earnings():
    # Retrieve all orders with payment completed
    completed_orders = Order.objects.filter(order_status='Completed')

    # Calculate total earnings
    total_earnings = completed_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    return total_earnings


   
class SalesReportView(View):
    def generate_report(self, start_date, end_date):
        # For daily report
        if start_date == end_date:
            daily_orders = Order.objects.filter(order_date=start_date)
            daily_revenue = daily_orders.filter(order_status="Completed").aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            daily_cancelled_orders = daily_orders.filter(order_status="Cancelled").count()
            
            params = {
                'daily_orders_count': daily_orders.count(),
                'daily_revenue': daily_revenue,
                'daily_cancelled_orders': daily_cancelled_orders,
            }

        # For weekly report
        elif (end_date - start_date).days == 6:
            weekly_start_date = start_date
            weekly_end_date = end_date
            weekly_orders = Order.objects.filter(order_date__range=[weekly_start_date, weekly_end_date])
            weekly_revenue = weekly_orders.filter(order_status="Completed").aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            weekly_cancelled_orders = weekly_orders.filter(order_status="Cancelled").count()

            params = {
                'weekly_orders_count': weekly_orders.count(),
                'weekly_revenue': weekly_revenue,
                'weekly_cancelled_orders': weekly_cancelled_orders,
            }

        # For yearly report
        elif start_date.year == end_date.year:
            yearly_orders = Order.objects.filter(order_date__year=start_date.year)
            yearly_revenue = yearly_orders.filter(order_status="Completed").aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            yearly_cancelled_orders = yearly_orders.filter(order_status="Cancelled").count()

            params = {
                'yearly_orders_count': yearly_orders.count(),
                'yearly_revenue': yearly_revenue,
                'yearly_cancelled_orders': yearly_cancelled_orders,
            }
        
        else:
                # Handle custom date range here
                custom_orders = Order.objects.filter(order_date__range=[start_date, end_date])
                custom_revenue = custom_orders.filter(order_status="Completed").aggregate(Sum('total_amount'))['total_amount__sum'] or 0
                custom_cancelled_orders = custom_orders.filter(order_status="Cancelled").count()

                params = {
                    'custom_orders_count': custom_orders.count(),
                    'custom_revenue': custom_revenue,
                    'custom_cancelled_orders': custom_cancelled_orders,
                }

        return params

    def render_to_pdf(self, context):
        template = get_template('admin_panel/sales_report.html')
        html = template.render(context)
        pdf_file = BytesIO()
        pisa.pisaDocument(BytesIO(html.encode("UTF-8")), pdf_file)
        return pdf_file.getvalue()

    def render_to_excel(self, context):
        workbook = xlsxwriter.Workbook(BytesIO())
        worksheet = workbook.add_worksheet('Sales Report')

        # Write headers
        headers = list(context.keys())
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        # Write data
        data = list(context.values())
        for row, row_data in enumerate(data, start=1):
            # Ensure row_data is iterable
            if not isinstance(row_data, (list, tuple)):
                row_data = [row_data]  # Convert to list if not already iterable
            for col, value in enumerate(row_data):
                worksheet.write(row, col, value)

        workbook.close()
        return workbook.filename



    def get(self, request, *args, **kwargs):
        report_type = request.GET.get('report_type', 'daily')
        report_format = request.GET.get('format', 'pdf')
        
        # Validate report type
        if report_type not in ['daily', 'weekly', 'monthly']:
            return HttpResponse("Invalid report type", status=400)
        
        # Validate report format
        if report_format not in ['pdf', 'excel']:
            return HttpResponse("Invalid report format", status=400)

        # Handle report generation based on both factors
        if report_type == 'daily':
            start_date = datetime.now().date()
            end_date = start_date
        elif report_type == 'weekly':
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=6)
        elif report_type == 'monthly':
            end_date = datetime.now().date()
            start_date = datetime(end_date.year, end_date.month, 1).date()
        
        context = self.generate_report(start_date, end_date)

        if report_format == 'pdf':
            pdf_content = self.render_to_pdf(context)
            response = HttpResponse(pdf_content, content_type='application/pdf')
            filename = "sales_report.pdf"
        else:  # report_format == 'excel'
            excel_content = self.render_to_excel(context)
            response = HttpResponse(excel_content.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            filename = "sales_report.xlsx"

        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


    

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



def change_status(request, order_id):
    if request.method == 'GET':
        new_status = request.GET.get('new_status')
        # Assuming you have a model named Order with a field named status
        order = Order.objects.get(id=order_id)
        valid_status_options = ['Pending', 'Shipped', 'Completed']
        # Checking the new_status against valid status options (case-insensitive and trimmed)
        if new_status.strip().title() in valid_status_options:
            # Capitalize the status
            new_status_title = new_status.strip().title()
            order.order_status = new_status_title
            # Save the delivery date if the new status is 'Completed'
            if new_status_title == 'Completed':
                order.delivery_date = datetime.now()
            order.save()
            # Adding success message
            messages.success(request, 'Status changed successfully.')
        else:
            # Adding error message for invalid status
            messages.error(request, 'Invalid status provided.')
    # Redirecting back to the same page or any desired page after status change
    return redirect(reverse('order_list'))
