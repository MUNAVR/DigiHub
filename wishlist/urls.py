from django.urls import path
from . import views

urlpatterns = [
    path('wishlist/',views.wishlist, name='wishlist'),
    path('add_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_wishlist'),
    path('remove_wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_wishlist'),
]