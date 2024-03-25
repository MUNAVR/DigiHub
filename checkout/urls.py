from django.urls import path
from checkout import views

urlpatterns = [
    path('checkout_page',views.checkout_page,name='checkout_page'), 
    path('apply_coupon', views.apply_coupon, name='apply_coupon'),


    path('place_order',views.place_order,name="place_order"),
    path('save_order_address/',views.save_order_address, name='save_order_address'),


    path('razorpay_payment',views.razorpay_payment,name='razorpay_payment'),
    path('handle_razorpay_success', views.handle_razorpay_success, name='handle_razorpay_success'),
    path('handle_razorpay_failure', views.handle_razorpay_failure, name='handle_razorpay_failure'),

    path("wallat_payment",views.wallet_payment,name="wallat_payment"),

    path("all_orders",views.all_orders,name="all_orders"),
    path("order_details/<id>",views.order_details,name="order_details"),
    path('cancel_order/<int:order_id>',views.cancel_order,name='cancel_order'),
    path("return_order/<int:order_id>",views.return_order,name="return_order"),

    path('continue_shoping/<id>',views.continue_shoping,name="continue_shoping"),
]