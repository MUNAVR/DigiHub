from django.urls import path
from .import views

urlpatterns =[
    path("wallet",views.wallet,name="wallet"),
    path("add_cash",views.add_cash,name="add_cash"),
    path("success_cash",views.handle_razorpay_success,name="success_cash"),
    

] 