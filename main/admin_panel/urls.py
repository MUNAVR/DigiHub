from django.urls import path
from admin_panel import views

# app_name='admin_side'

urlpatterns = [
    path('admin_login',views.admin_login,name="admin_login"),
    path('admin_index',views.admin_index,name="admin_index"),
    path('customer',views.customer,name="customer"),
    path('admin_logout',views.admin_logout,name="admin_logout"),
    path('customer_edit/<id>',views.customer_edit,name='customer_edit'),
    path('delete/<id>',views.customer_delete,name='cust_delete'),
    path('block/<id>',views.block_user, name='user_block'),
    path('unblock/<id>',views.unblock_user, name='user_block')
]