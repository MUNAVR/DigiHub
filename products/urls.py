from django.urls import path
from .import views

urlpatterns =[
    path('product_list',views.Product_list,name="product_list"),
    path('product_grid',views.product_grid,name="product_grid"),

    path('product_attributes',views.product_attributes,name="product_attributes"),
    path('attribute_edit/<id>',views.attribute_edit,name="attribute_edit"),
    path('attribute_delete/<id>',views.attribute_delete),

    path('product_add',views.Product_add,name="product_add"),
    path('product_edit/<id>',views.product_edit,name='product_edit'),
    path('product_delete/<id>',views.product_delete),

    path('variant_add',views.variant_add,name="variant_add"),
    path('variant_list',views.variant_list,name="variant_list"),
    path('variant_delete/<id>',views.variant_delete),
    path('variant_edit/<id>',views.variant_edit,name="variant_edit"),

    path('search_mobiles',views.search_mobiles,name="search_mobiles"),

    # user_side
    

    
]