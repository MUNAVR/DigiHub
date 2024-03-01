from django.urls import path
from checkout import views

urlpatterns = [
    path('store_cart_data/', views.store_cart_data,name='store_cart_data'),
    path('checkout_page',views.checkout_page,name='checkout_page'), 
]