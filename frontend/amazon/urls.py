from django.urls import path
from amazon import views

urlpatterns = [
    path('', views.user_login, name = 'login'),
    path('register/', views.register, name='register'),
    # path('login/', views.user_login, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.user_logout, name='logout'),
    path('placeOrder/', views.placeANewOrder, name='placeOrder'),
    path('orderSuccess/', views.orderSuccess, name='orderSuccess'),
    path('productList/', views.productList, name='productList'),
    path('viewCart/', views.viewCart, name='viewCart'),
    path('orders/', views.orderList, name='orderList'),
    path('orders/<int:order_id>/', views.orderDetail, name='orderDetail'),
]