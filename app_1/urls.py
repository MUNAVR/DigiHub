from django.urls import path
from . import views

app_name="user"

urlpatterns = [
    path('login', views.login,name='login'),
    path('forgot_pass',views.forgot_pass,name="forgot_pass"),
    
    path('signup',views.signup,name='signup'),
    path('logout',views.logout,name='logout'),
    path('',views.index,name='index'),
    path('sort_products/', views.sort_products, name='sort_products'),
    # path('sent_otp',views.sent_otp,name="send_otp"),
    path('verify_otp',views.verify_otp,name="verify_otp"),
    path('resend_otp',views.resend_otp,name="otp"),
    path('product_details/<id>',views.product_details,name="product_details"),
    path('get_product_details',views.get_product_details, name='get_product_details'),

    


    path('user-profile',views.user_profile,name="user_profile"),
    path('add_adress1',views.add_address1,name="add_address1"),
    path('add_adress2',views.add_address2,name="add_address2"),
    path('delete_address/', views.delete_address, name='delete_address'),
    path('delete_address2/', views.delete_address2, name='delete_address2'),
    path('change_pass',views.change_pass,name="change_pass"),

    
]
