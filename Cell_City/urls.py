from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name ='home'),
    path('accounts/profile/', views.home, name ='home'),
    path('products/<int:brand_id>/', views.products, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('increase_quantity/<int:cart_item_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease_quantity/<int:cart_item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-mode/<int:order_id>/', views.payment_mode, name='payment_mode'),
    path('order-confirmation/<str:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('invoice/<str:order_id>/', views.view_invoice, name='invoice'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search_results, name='search_results'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('feedback/', views.feedback, name='feedback'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('ai-recommendation/', views.ai_recommendation, name='ai_recommendation'),
    path('chatbot/', views.chatbot, name='chatbot'),
    
]


