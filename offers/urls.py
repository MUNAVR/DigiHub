from django.urls import path
from .import views

urlpatterns =[
    path('product_offer_list',views.product_offer_list,name="product_offer_list"),
    path('brand_offer_list',views.brand_offer_list,name="brand_offer_list"),
    path('referral_offer_list',views.referral_offer_list,name="referral_offer_list"),
    path("create_offer",views.create_offer,name="create_offer"),

    path('get_offers/', views.get_offers, name='get_offers'),
] 