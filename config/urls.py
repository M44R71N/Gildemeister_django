"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from core import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.register_view, name='register'),
    path('admin/', admin.site.urls),
    path('menu/', views.menu_view, name='menu'),
    path('productos/', views.productos_view, name='productos'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('canjeo/', views.canjeo_view, name='canjeo'),
    path('perfil/canjear/<int:recompensa_id>/', views.canjear_recompensa_view, name='canjear_recompensa'),
    path('carrito/', views.carrito_view, name='carrito'),
    path('carrito/agregar/<str:producto_id>/', views.agregar_carrito_view, name='agregar_carrito'),
    path('carrito/disminuir/<str:producto_id>/', views.disminuir_carrito_view, name='disminuir_carrito'),
    path('carrito/eliminar/<str:producto_id>/', views.eliminar_carrito_view, name='eliminar_carrito'),
    path('carrito/finalizar/', views.finalizar_compra_view, name='finalizar_compra'),
]
