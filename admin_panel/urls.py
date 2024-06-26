from django.urls import path
from admin_panel import views



urlpatterns = [
    path('admin_login',views.admin_login,name="admin_login"),
    path('admin_index',views.admin_index,name="admin_index"),

    
    path('get-monthly-sales/',views.get_monthly_sales, name='get_monthly_sales'),
    path('get-yearly-sales/',views.get_yearly_sales, name='get_yearly_sales'),

    path('sales-report/',views.SalesReportView.as_view(), name='sales-report'),

    path('customer',views.customer,name="customer"),
    path('admin_logout',views.admin_logout,name="admin_logout"),
    path('customer_edit/<id>',views.customer_edit,name='customer_edit'),
    path('delete/<id>',views.customer_delete,name='cust_delete'),
    path('block/<int:id>/', views.block_user, name='block_user'),
    path('unblock/<int:id>/', views.unblock_user, name='unblock_user'),

    path("order_list",views.order_list,name="order_list"),
    path("order_cancel/<order_id>",views.reject_orderAdmin,name="order_cancel"),
    path("change_status/<order_id>",views.change_status,name="change_status"),

    path('best_selling_product',views.best_selling_product, name='best_selling_product'),
    path('best_selling_brand',views.best_selling_brand, name='best_selling_brand'),

    
]