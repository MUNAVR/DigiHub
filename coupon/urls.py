from django.urls import path
from coupon import views

urlpatterns = [
    path("create_coupon",views.admin_create_coupon,name="create_coupon"),
    path("coupen_list",views.admin_manage_coupons,name="coupen_list"),
    path('change_active/<int:coupon_id>/', views.change_active, name='change_active'),
    path("delete_coupon/<id>",views.coupon_delete,name="delete_coupon"),


]