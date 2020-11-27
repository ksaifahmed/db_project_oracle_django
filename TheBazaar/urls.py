"""TheBazaar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import home.views as home_view
import categories.views as categ_view
import product.views as prod_views
import register.views as reg_views
import login.views as login_views
import cart.views as cart_view
import my_profile.views as profile_view
import purchases.views as purchases_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view.load_home),
    path('categories/<slug:slug>/', categ_view.load_category),
    path('product/<slug:slug>/', prod_views.load_product),
    path('register/', reg_views.load_data, name='register'),
    path('login/', login_views.load_login, name='login'),
    path('logout/', login_views.del_session),
    path('cart/', cart_view.load_cart),
    path('cart-removal/<slug:slug>/', cart_view.del_cart_item),
    path('profile/', profile_view.load_profile),
    path('purchases/', purchases_view.load_orders)
]
