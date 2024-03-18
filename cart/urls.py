from django.urls import path
from cart import views

urlpatterns = [
    path('shop_cart',views.shop_cart,name="shop_cart"),
    path('add_cart/<int:variant_id>/', views.add_cart, name='add_cart'),
    path('delete_cart_item/<int:cart_item_id>/',views.delete_cart_item,name="delete_cart_item"),
    path('delete_all',views.delete_all,name="delete_all"),
    path('update_cart_quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    
    # checkout ____________________________________________
    
]