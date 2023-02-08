from django.urls import path, re_path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.shortcuts import render, redirect
from django.urls import reverse


app_name = 'ecommerce'

urlpatterns = [
    path('lookbook/', views.LookbookView.as_view(), name='lookbook'),

    path('checkout/<str:shipping_method>',views.CheckOutView.as_view(),name='checkout'),
    
    path('', views.redirect_home),
    path('shop/', views.ShopView.as_view(), name='shop-all'),
    path('shop/<slug:slug_url>/', views.ShopCategoryView.as_view(), name='shop-category'),

    path('product/<str:slug>/',views.ProductDetailView.as_view(),name='product-detail'),

    path('cart/',views.CartView.as_view(),name='shopping-cart'),

    # path for AJAX
    path('ajax/shop/filter-data/', views.filter_data_all,name='filter-data-all'),
    path('ajax/<slug:slug_url>/filter-data/', views.filter_data_category,name='filter-data'),
    path('ajax/<slug:slug>/color-filter-product/', views.product_color_choice,name='color-filter-data'),
    path('ajax/<slug:slug>/color-size-filter-product/', views.quantity_choice,name='color-filter-data'),

    path('ajax/add-to-cart/',views.add_to_cart,name='add-to-cart'),
    path('ajax/delete-from-cart/',views.delete_from_cart,name='delete-from-cart'),
    path('ajax/update-cart/',views.update_cart,name='update_cart'),

]

