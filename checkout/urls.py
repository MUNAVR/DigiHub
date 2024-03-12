from django.urls import path
from checkout import views

urlpatterns = [
    path('checkout_page',views.checkout_page,name='checkout_page'), 
    path('place_order',views.place_order,name="place_order"),

    path('razorpay_payment',views.razorpay_payment,name='razorpay_payment'),
    path('handle_razorpay_success', views.handle_razorpay_success, name='handle_razorpay_success'),
    path('handle_razorpay_failure', views.handle_razorpay_failure, name='handle_razorpay_failure'),

    path("wallat_payment",views.wallet_payment,name="wallat_payment"),

    path("all_orders",views.all_orders,name="all_orders"),
    path("order_details/<id>",views.order_details,name="order_details"),
    path('cancel_order/<int:order_id>',views.cancel_order,name='cancel_order'),
]