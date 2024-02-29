from django.urls import path
from category import views

urlpatterns =[


    path('category',views.category,name="category"),
    path('category_edit/<id>',views.category_edit,name="category_edit"),
    path('category_delete/<id>',views.category_delete),


    # Brand-----------------------------------------------------------------------------------------
    
    path('admin_brands',views.brands_manage,name="admin_brands"),
    path('brand_edit/<id>',views.brand_edit,name="brand_edit"),
    path('brand_delete/<id>',views.brand_delete)
]
