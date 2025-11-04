from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('inventory/', views.manage_inventory, name='manage_inventory'),
    path('inventory/add/', views.add_product, name='add_product'),
    path('inventory/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('inventory/sales/', views.sales_report, name='sales_report'),
    path('inventory/search/', views.search_product, name='search_product'),
]