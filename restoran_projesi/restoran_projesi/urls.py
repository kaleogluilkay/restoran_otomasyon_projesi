"""
URL configuration for restoran_projesi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path,include
from django.contrib.auth import views as auth_views
from restaurant import views




urlpatterns = [
    path('', views.index, name='index'),
    path('garson-panel/', views.garson_panel, name='garson_panel'),
    path('sef-panel/', views.sef_panel, name='sef_panel'),
    path('admin/', admin.site.urls),
    path('login/', views.custom_login, name='login'),
    path('giris-yonlendirme', views.giris_yonlendirme, name='giris_yonlendirme'),
    path('login/', auth_views.LoginView.as_view(template_name='restaurant/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('', include('restaurant.urls')),  # uygulama url'leri
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('sef-panel/', views.sef_panel, name='sef_panel'),
    path('siparis/<int:siparis_id>/durum-guncelle/', views.siparis_durum_guncelle, name='siparis_durum_guncelle'),
    path('garson-panel/', views.garson_panel, name='garson_panel'),
    path('yeni-siparis/', views.yeni_siparis, name='yeni_siparis'),
    path('sef/malzeme-kullan/<int:siparis_id>/', views.malzeme_kontrol_ve_kullan, name='malzeme_kullan'),
    path('sef/tarif-ekle/', views.tarif_ekle, name='tarif_ekle'),

]

