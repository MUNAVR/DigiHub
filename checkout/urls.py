from django.urls import path
from checkout import views

urlpatterns = [
    path('checkout_page',views.checkout_page,name='checkout_page'), 
]