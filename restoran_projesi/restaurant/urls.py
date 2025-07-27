from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('menu/', views.menu_listesi, name='menu_listesi'),
    path('siparis/', views.siparis_olustur, name='siparis_olustur'),
    path('siparis/', views.siparis_listesi, name='siparis_listesi'),
    path('rapor/gunluk-satis/', views.gunluk_satis_raporu, name='gunluk_satis_raporu'),
    path('garson-panel/', views.garson_panel, name='garson_panel'),
    path('garson-siparislerim/', views.siparislerim, name='siparislerim'),
    path('siparis-gonder/', views.siparis_gonder, name='siparis_gonder'),
    path('siparis-odendi/<int:siparis_id>/', views.siparis_odendi, name='siparis_odendi'),
    path('siparislerim/', views.siparislerim, name='siparislerim'),
    path('sef/', views.sef_panel, name='sef_panel'),
    path('sef/malzeme-kullan/<int:siparis_id>/', views.malzeme_kontrol_ve_kullan, name='malzeme_kullan'),
    path('sef/siparis-durum-guncelle/', views.siparis_durum_guncelle, name='siparis_durum_guncelle'),
    path('kategori/<str:kategori>/urunler/', views.kategori_urunleri_getir, name='kategori_urunleri_getir'),
    path('rapor/gelir/', views.gelir_raporu_sayfasi, name='gelir_raporu'),
    path('rapor/gelir-veri/', views.gelir_grafik_veri, name='gelir_grafik_veri'),

    path('logout/', views.logout_view, name='logout'),
    path('login/', views.custom_login, name='login'),
    ]

