from django.urls import path
from .import views

urlpatterns =[
    path('referral_offer_list',views.display_referral_offers,name="referral_offer_list"),
    path("create_offer",views.create_referral_offer,name="create_offer"),
    path('referral_active/<int:offer_id>/', views.referral_active, name="referral_active"),

] 