from django.contrib.auth import views as auth_views
from django.urls import path 
from . import views 
from . import forms

urlpatterns = [
    
    # صفحات عمومی
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('team/', views.team_view, name='team'),

    # احراز هویت و پروفایل
    path('profile/', views.profile_view, name='profile'),
    path('edit_profile/', views.edit_profile_view, name='edit_profile'),   
    path('unauthorized/', views.unauthorized_view, name='unauthorized'),

    # کتاب‌ها و نقدها
    path('book_list/', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),    
    path('add_book/', views.add_book, name='add_book'),
    path('edit_book/<int:pk>/', views.edit_book, name='edit_book'),
    path('books/<int:pk>/delete/', views.delete_book, name='delete_book'),
    path('books/<int:pk>/review/', views.add_review, name='add_review'),
    path('review/edit/<int:pk>/', views.edit_review_view, name='edit_review'),
    path('review/delete/<int:pk>/', views.delete_review_view, name='delete_review'),    
    path('my-reviews/', views.my_reviews_view, name='my_reviews'),
    path('my-books/', views.my_books_view, name='my_books'),
    
    # علاقه‌مندی‌ها
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:pk>/', views.toggle_wishlist, name='toggle_wishlist'),

    # سبد خرید و سفارش
    path('add_to_cart/<int:pk>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/decrease/<int:pk>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove_from_cart/<int:pk>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('order-receipt/', views.order_receipt, name='order_receipt'),
    path('pay/', views.request_payment, name='request_payment'),
    path('verify/', views.verify_payment, name='verify_payment'),
    path('payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),

    # بازیابی رمز عبور
    path('password_reset/',auth_views.PasswordResetView.as_view(template_name='shop/password_reset.html',form_class=forms.CustomPasswordResetForm),name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='shop/password_reset_done.html'), name='password_reset_done'),
   path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='shop/password_reset_confirm.html',form_class=forms.CustomSetPasswordForm),name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='shop/password_reset_complete.html'), name='password_reset_complete'),
]


