from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static


from .views import profile_update



urlpatterns = [
    
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('shop1/', views.shop1, name='shop1'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('dashboard/', views.user_dashboard, name='dashboard'),

    path('profile/', views.profile, name='profile'),
    path('body_profile/', views.profile, name='body_profile'),

    path('diet/', views.diet_plan, name='diet'),
    path("profile_update/", views.profile_update, name="profile_update"),

    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('home/', views.home, name='home'),
    path('nav/', views.nav, name='nav'),
    



    
    path('product/<str:type>/<int:id>/', views.product_detail, name='product_detail'),

    path('add-to-cart/<str:type>/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('buy-now/<str:type>/<int:id>/', views.buy_now, name='buy_now'),
    
path('cart/', views.cart_page, name='cart'),

path('update-cart/<str:key>/', views.update_cart, name='update_cart'),
path('remove-from-cart/<str:key>/', views.remove_from_cart, name='remove_from_cart'),
path("checkout/", views.checkout, name="checkout"),
path("payment-success/<int:order_id>/", views.payment_success, name="payment_success"),

path("orders/", views.order_history, name="order_history"),
path(
        "invoice/<int:order_id>/",
        views.download_invoice,
        name="download_invoice"
    ),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




